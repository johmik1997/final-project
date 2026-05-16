import requests
from django.db.models import Avg, Count, Q
from django.utils.translation import gettext as _
from uuid import UUID

from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from django.contrib.auth import update_session_auth_hash
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import os
from django.db.models import Prefetch
from material_mgt.models import *
from material_mgt.serializers import *
from material_mgt.services import generate_pdf_cover_image
from transactions.models import Borrow, Reservation
from user_mgt.access import (
    get_user_library,
    has_global_material_access,
    is_super_admin,
    normalize_role,
)
from user_mgt.permissions import *
# Create your views here.


def _parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _resolve_material_or_error(material_type, material_id):
    material_type_norm = str(material_type or "").strip().lower()
    material_id_str = str(material_id or "").strip()

    try:
        material_uuid = UUID(material_id_str)
    except (TypeError, ValueError):
        raise ValidationError({"material_id": _("Invalid material id.")})

    if material_type_norm == "physical":
        material = PhysicalMaterial.objects.filter(pk=material_uuid).first()
        if not material:
            raise ValidationError({"material_id": "Physical material not found."})
        return material_type_norm, material

    if material_type_norm == "digital":
        material = DigitalMaterial.objects.filter(pk=material_uuid).first()
        if not material:
            raise ValidationError({"material_id": "Digital material not found."})
        return material_type_norm, material

    raise ValidationError({"material_type": "Use either 'physical' or 'digital'."})


def _user_can_access_material(user, material):
    if has_global_material_access(user):
        return True
    user_library = get_user_library(user)
    return bool(user_library and getattr(material, "library_id", None) == user_library.id)


class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


def _get_staff_profile_or_error(user):
    staff_roles = {"STACKSTAFF", "TECHNICALSTAFF", "FRONTDESKSTAFF", "ADMIN", "SUPERADMIN"}
    if normalize_role(getattr(user, "role", None)) not in staff_roles:
        raise ValidationError({"detail": "Only staff-role users can create materials."})
    return user

class PhysicalMaterialViewSet(ModelViewSet):
    queryset = PhysicalMaterial.objects.select_related("library", "created_by").prefetch_related(
        Prefetch("feedbacks", queryset=MaterialFeedback.objects.select_related("user").order_by("-updated_at"))
    ).annotate(
        average_rating=Avg("feedbacks__rating"),
        ratings_count=Count("feedbacks"),
    ).order_by("title", "id")
    serializer_class = PhysicalMaterialSerializer
    # permission_classes = [IsAuthenticated, IsTechnicalStaffForWrite]

    def get_queryset(self):
        queryset = super().get_queryset()
        if has_global_material_access(self.request.user):
            return queryset

        actor_library = get_user_library(self.request.user)
        if not actor_library:
            return queryset.none()
        return queryset.filter(library=actor_library)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_profile = _get_staff_profile_or_error(request.user)
        actor_library = get_user_library(request.user)
        if not actor_library and not is_super_admin(request.user):
            raise ValidationError({"library": "Your account is not assigned to a library yet."})

        data = serializer.validated_data
        total_copies = int(data.get("total_copies") or 0)
        if total_copies < 1:
            raise ValidationError({"total_copies": "total_copies must be at least 1."})

        available_copies = data.get("available_copies")
        if available_copies is None:
            available_copies = total_copies
        elif int(available_copies) > total_copies:
            raise ValidationError(
                {"available_copies": "available_copies cannot exceed total_copies."}
            )

        material = serializer.save(
            created_by=staff_profile,
            available_copies=available_copies,
            library=data.get("library") if is_super_admin(request.user) else actor_library,
        )
        output = self.get_serializer(material)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        actor_library = get_user_library(self.request.user)
        if not actor_library and not is_super_admin(self.request.user):
            raise ValidationError({"library": "Your account is not assigned to a library yet."})
        serializer.save(
            library=serializer.validated_data.get("library") if is_super_admin(self.request.user) else actor_library
        )


class DigitalMaterialViewSet(ModelViewSet):
    queryset = DigitalMaterial.objects.select_related("library", "created_by").prefetch_related(
        Prefetch("feedbacks", queryset=MaterialFeedback.objects.select_related("user").order_by("-updated_at"))
    ).annotate(
        average_rating=Avg("feedbacks__rating"),
        ratings_count=Count("feedbacks"),
    ).order_by("title", "id")
    serializer_class = DigitalMaterialSerializer
    # permission_classes = [IsAuthenticated, IsTechnicalStaffForWrite]

    def get_queryset(self):
        queryset = super().get_queryset()
        if has_global_material_access(self.request.user):
            return queryset

        actor_library = get_user_library(self.request.user)
        if not actor_library:
            return queryset.none()
        return queryset.filter(library=actor_library)

    def perform_create(self, serializer):
        actor_library = get_user_library(self.request.user)
        if not actor_library and not is_super_admin(self.request.user):
            raise ValidationError({"library": "Your account is not assigned to a library yet."})
        instance = serializer.save(
            created_by=_get_staff_profile_or_error(self.request.user),
            library=serializer.validated_data.get("library") if is_super_admin(self.request.user) else actor_library,
        )
        if not instance.cover_image and generate_pdf_cover_image(instance):
            instance.save(update_fields=["cover_image", "cover_generated_at"])

    def perform_update(self, serializer):
        actor_library = get_user_library(self.request.user)
        if not actor_library and not is_super_admin(self.request.user):
            raise ValidationError({"library": "Your account is not assigned to a library yet."})
        instance = serializer.save(
            library=serializer.validated_data.get("library") if is_super_admin(self.request.user) else actor_library
        )
        if not instance.cover_image and generate_pdf_cover_image(instance):
            instance.save(update_fields=["cover_image", "cover_generated_at"])


class MaterialFeedbackViewSet(ModelViewSet):
    serializer_class = MaterialFeedbackSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = MaterialFeedback.objects.select_related("user", "physical_material", "digital_material")

    def get_queryset(self):
        queryset = self.queryset

        material_type = self.request.query_params.get("material_type")
        material_id = self.request.query_params.get("material_id")
        mine_only = _parse_bool(self.request.query_params.get("mine"), default=False)

        if mine_only:
            queryset = queryset.filter(user=self.request.user)

        if bool(material_type) ^ bool(material_id):
            raise ValidationError(
                {"detail": "Provide material_type and material_id together."}
            )

        if material_type and material_id:
            material_type_norm = material_type.strip().lower()
            if material_type_norm == "physical":
                queryset = queryset.filter(physical_material_id=material_id)
            elif material_type_norm == "digital":
                queryset = queryset.filter(digital_material_id=material_id)
            else:
                raise ValidationError({"material_type": "Use either 'physical' or 'digital'."})

        return queryset

    def perform_create(self, serializer):
        target_material = serializer.validated_data.get("physical_material") or serializer.validated_data.get("digital_material")
        if target_material and not _user_can_access_material(self.request.user, target_material):
            raise ValidationError({"detail": "You can only comment on materials from your library."})
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path=r"by-material/(?P<material_type>[^/.]+)/(?P<material_id>[^/.]+)")
    def by_material(self, request, material_type=None, material_id=None):
        if not material_type or not material_id:
            raise ValidationError({"detail": "material_type and material_id are required."})

        material_type_norm, material = _resolve_material_or_error(material_type, material_id)
        if material_type_norm == "physical":
            queryset = self.queryset.filter(physical_material=material)
        else:
            queryset = self.queryset.filter(digital_material=material)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaterialFavoriteViewSet(ModelViewSet):
    serializer_class = MaterialFavoriteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = MaterialFavorite.objects.select_related("user", "physical_material", "digital_material")

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        material_type = self.request.query_params.get("material_type")
        material_id = self.request.query_params.get("material_id")
        if bool(material_type) ^ bool(material_id):
            raise ValidationError(
                {"detail": "Provide material_type and material_id together."}
            )
        if material_type and material_id:
            material_type_norm = material_type.strip().lower()
            if material_type_norm == "physical":
                queryset = queryset.filter(physical_material_id=material_id)
            elif material_type_norm == "digital":
                queryset = queryset.filter(digital_material_id=material_id)
            else:
                raise ValidationError({"material_type": "Use either 'physical' or 'digital'."})

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        physical_material = serializer.validated_data.get("physical_material")
        digital_material = serializer.validated_data.get("digital_material")
        target_material = physical_material or digital_material
        if target_material and not _user_can_access_material(request.user, target_material):
            raise ValidationError({"detail": "You can only favorite materials from your library."})

        favorite, created = MaterialFavorite.objects.get_or_create(
            user=request.user,
            physical_material=physical_material,
            digital_material=digital_material,
        )

        output = self.get_serializer(favorite)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MaterialBookmarkViewSet(ModelViewSet):
    serializer_class = MaterialBookmarkSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = MaterialBookmark.objects.select_related("user", "physical_material", "digital_material")

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        material_type = self.request.query_params.get("material_type")
        material_id = self.request.query_params.get("material_id")
        if bool(material_type) ^ bool(material_id):
            raise ValidationError(
                {"detail": "Provide material_type and material_id together."}
            )
        if material_type and material_id:
            material_type_norm = material_type.strip().lower()
            if material_type_norm == "physical":
                queryset = queryset.filter(physical_material_id=material_id)
            elif material_type_norm == "digital":
                queryset = queryset.filter(digital_material_id=material_id)
            else:
                raise ValidationError({"material_type": "Use either 'physical' or 'digital'."})

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        physical_material = serializer.validated_data.get("physical_material")
        digital_material = serializer.validated_data.get("digital_material")
        target_material = physical_material or digital_material
        if target_material and not _user_can_access_material(request.user, target_material):
            raise ValidationError({"detail": "You can only bookmark materials from your library."})

        bookmark, created = MaterialBookmark.objects.get_or_create(
            user=request.user,
            physical_material=physical_material,
            digital_material=digital_material,
        )

        output = self.get_serializer(bookmark)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MaterialInteractionStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        material_type = request.query_params.get("material_type")
        material_id = request.query_params.get("material_id")

        if not material_type or not material_id:
            raise ValidationError({"detail": "material_type and material_id are required."})

        material_type_norm, material = _resolve_material_or_error(material_type, material_id)
        if not _user_can_access_material(request.user, material):
            raise ValidationError({"detail": "You can only access interaction stats for materials in your library."})

        feedback_qs = MaterialFeedback.objects.all()
        favorites_qs = MaterialFavorite.objects.all()
        bookmarks_qs = MaterialBookmark.objects.all()

        if material_type_norm == "physical":
            feedback_qs = feedback_qs.filter(physical_material=material)
            favorites_qs = favorites_qs.filter(physical_material=material)
            bookmarks_qs = bookmarks_qs.filter(physical_material=material)
            mine_filter = {"physical_material": material, "user": request.user}
        else:
            feedback_qs = feedback_qs.filter(digital_material=material)
            favorites_qs = favorites_qs.filter(digital_material=material)
            bookmarks_qs = bookmarks_qs.filter(digital_material=material)
            mine_filter = {"digital_material": material, "user": request.user}

        aggregate = feedback_qs.aggregate(
            average_rating=Avg("rating"),
            ratings_count=Count("id"),
            comments_count=Count("id", filter=~Q(comment="")),
        )

        my_feedback = MaterialFeedback.objects.filter(**mine_filter).first()

        return Response(
            {
                "material_type": material_type_norm,
                "material_id": str(material.id),
                "material_title": material.title,
                "average_rating": round(float(aggregate["average_rating"] or 0), 2),
                "ratings_count": int(aggregate["ratings_count"] or 0),
                "comments_count": int(aggregate["comments_count"] or 0),
                "favorites_count": favorites_qs.count(),
                "bookmarks_count": bookmarks_qs.count(),
                "is_favorited": MaterialFavorite.objects.filter(**mine_filter).exists(),
                "is_bookmarked": MaterialBookmark.objects.filter(**mine_filter).exists(),
                "my_rating": my_feedback.rating if my_feedback else None,
                "my_comment": my_feedback.comment if my_feedback else "",
            },
            status=status.HTTP_200_OK,
        )


def _get_openai_api_key():
    return os.getenv("OPENAI_API_KEY", "").strip()


def _get_openai_model(env_name, default="gpt-5-mini"):
    return os.getenv(env_name, default).strip() or default


def _extract_openai_text(payload):
    output_text = str(payload.get("output_text", "") or "").strip()
    if output_text:
        return output_text

    text_parts = []
    for item in payload.get("output", []) or []:
        for content in item.get("content", []) or []:
            text = str(content.get("text", "") or "").strip()
            if text:
                text_parts.append(text)

    return "\n".join(text_parts).strip()


def _request_openai_text(*, model, prompt, max_output_tokens):
    api_key = _get_openai_api_key()
    if not api_key:
        return {
            "success": False,
            "status": status.HTTP_503_SERVICE_UNAVAILABLE,
            "error": "AI service is not configured.",
            "text": "",
        }

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": prompt,
                "max_output_tokens": max_output_tokens,
            },
            timeout=30,
        )
    except requests.RequestException:
        return {
            "success": False,
            "status": status.HTTP_502_BAD_GATEWAY,
            "error": "Failed to reach AI provider.",
            "text": "",
        }

    if response.status_code >= 400:
        try:
            provider_error = response.json().get("error", {}).get("message", "")
        except ValueError:
            provider_error = ""

        return {
            "success": False,
            "status": status.HTTP_502_BAD_GATEWAY,
            "error": provider_error or "AI provider returned an error.",
            "text": "",
        }

    try:
        payload = response.json()
    except ValueError:
        return {
            "success": False,
            "status": status.HTTP_502_BAD_GATEWAY,
            "error": "Invalid AI provider response.",
            "text": "",
        }

    return {
        "success": True,
        "status": status.HTTP_200_OK,
        "error": "",
        "payload": payload,
        "text": _extract_openai_text(payload),
    }


def _build_chat_prompt(prompt, history=None):
    sanitized_history = history if isinstance(history, list) else []
    lines = [
        "You are a helpful virtual assistant for a university digital library system.",
        "Answer clearly and politely.",
        "Focus on library policies, reservations, borrowing, returns, fines, and material discovery.",
        "If you are unsure, say so and avoid inventing facts.",
        "",
        "Conversation so far:",
    ]

    for item in sanitized_history[-10:]:
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if not content:
            continue
        speaker = "User" if role == "user" else "Assistant"
        lines.append(f"{speaker}: {content}")

    lines.append(f"User: {prompt}")
    lines.append("Assistant:")
    return "\n".join(lines)


def _build_library_context(user):
    if not user or not user.is_authenticated:
        return {}

    borrows = Borrow.objects.select_related("material").filter(member=user).exclude(status="RETURNED").order_by("due_date")[:5]
    reservations = Reservation.objects.select_related("material_id").filter(member=user, status="RESERVED").order_by("reserve_date")[:5]
    available_books = PhysicalMaterial.objects.filter(available_copies__gt=0).order_by("title")[:10]

    return {
        "borrowed_materials": [
            {"title": row.material.title, "due_date": row.due_date.date().isoformat(), "status": row.status}
            for row in borrows
        ],
        "reservations": [
            {"title": row.material_id.title, "expiry_date": row.expiry_date.date().isoformat(), "status": row.status}
            for row in reservations
        ],
        "available_books": [row.title for row in available_books],
    }


class LibraryAssistantChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        prompt = str(request.data.get("prompt", "")).strip()
        history = request.data.get("history", [])
        language = str(request.data.get("language", "en")).strip().lower()

        if not prompt:
            raise ValidationError({"prompt": _("Prompt is required.")})

        model = _get_openai_model("OPENAI_CHAT_MODEL")
        context_prefix = (
            f"Preferred response language: {'Amharic' if language.startswith('am') else 'English'}.\n"
            f"Library data context: {_build_library_context(request.user)}\n"
        )
        result = _request_openai_text(
            model=model,
            prompt=context_prefix + _build_chat_prompt(prompt, history),
            max_output_tokens=400,
        )

        if not result["success"]:
            return Response({"detail": result["error"]}, status=result["status"])

        message = result["text"] or _("I am sorry, I could not generate an answer right now.")
        return Response({"message": message, "model": model}, status=status.HTTP_200_OK)




class GenerateMaterialDescriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        title = str(request.data.get("title", "")).strip()
        author = str(request.data.get("author", "")).strip()

        if not title or not author:
            raise ValidationError({"detail": "Both title and author are required."})

        model = _get_openai_model("OPENAI_DESCRIPTION_MODEL")

        prompt = (
            f"Title: {title}\n"
            f"Author: {author}\n\n"
            "Write a concise, helpful library catalog description (80-130 words). "
            "Use clear, neutral language and avoid inventing specific facts."
        )

        result = _request_openai_text(
            model=model,
            prompt=prompt,
            max_output_tokens=220,
        )

        if not result["success"]:
            return Response({"detail": result["error"]}, status=result["status"])

        description = result["text"]

        if not description:
            description = f"{title} by {author} is a library material available for borrowing."

        return Response(
            {
                "description": description,
                "model": model,
            },
            status=status.HTTP_200_OK,
        )
