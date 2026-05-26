from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from django.db.models import Q

from ebook.cache_utils import CachedListRetrieveMixin, cache_api_response
from material_mgt.cache import LIBRARY_CACHE_NAMESPACE, invalidate_library_caches
from .access import get_user_library, is_admin_like, is_super_admin, normalize_role
from .models import CampusStudent, Library, User, LibraryPolicy, Notification
from .permissions import CanCreateUsers, CanDeleteUsers, IsSuperAdminForWrite
from .serializers import (
    CampusStudentSerializer,
    StudentSelfRegisterSerializer,
    AdminUserListSerializer,
    ChangePasswordSerializer,
    FirstLoginChangePasswordSerializer,
    ConfirmResetOTPSerializer,
    ForgotPasswordSerializer,
    LibrarySerializer,
    LibraryPolicySerializer,
    ResetPasswordSerializer,
    UserListSerializer,
    UserMeSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    NotificationSerializer,
)

from rest_framework_simplejwt.views import TokenObtainPairView

# --- Authentication Views ---

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            raise ValidationError({"old_password": "Old password is incorrect."})
        user.set_password(serializer.validated_data["new_password"])
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password"])
        update_session_auth_hash(request, user)
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class FirstLoginChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FirstLoginChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Password updated.", "must_change_password": False}, status=status.HTTP_200_OK)


# --- Password Reset Flow ---

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "If an account with that email exists, a password reset OTP has been sent."},
            status=status.HTTP_200_OK,
        )


class ConfirmResetOTPAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ConfirmResetOTPSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                    "expires_in": {"type": "integer"},
                    "confirm_token": {"type": "string"},
                },
            }
        },
    )
    def post(self, request):
        serializer = ConfirmResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        
        response = Response(
            {
                "detail": "OTP confirmed.",
                "expires_in": data["expires_in"],
                "confirm_token": data["confirm_token"],
            },
            status=status.HTTP_200_OK,
        )
        
        # Set the confirmation token in an HttpOnly cookie for security
        response.set_cookie(
            "password_reset_confirm_token",
            data["confirm_token"],
            max_age=data["expires_in"],
            httponly=True,
            samesite="Lax",
            secure=not settings.DEBUG,  # True in production
        )
        return response


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    )
    def post(self, request):
        # We pass the request to context so the serializer can read the cookie
        serializer = ResetPasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response = Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        # Clean up the session cookie after success
        response.delete_cookie("password_reset_confirm_token")
        return response


class StudentSelfRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=StudentSelfRegisterSerializer,
        responses={201: UserMeSerializer},
    )
    def post(self, request):
        serializer = StudentSelfRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        payload = UserMeSerializer(user, context={"request": request}).data
        return Response(
            {
                "detail": "Registration successful. You can now sign in with your student ID.",
                "user": payload,
            },
            status=status.HTTP_201_CREATED,
        )


class CampusStudentViewSet(ModelViewSet):
    queryset = CampusStudent.objects.all().order_by("id_number")
    serializer_class = CampusStudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["id_number", "full_name", "phone", "department"]

    def _ensure_write_access(self):
        if not is_admin_like(self.request.user):
            raise ValidationError("Only ADMIN or SUPER ADMIN can manage campus student records.")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        self._ensure_write_access()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._ensure_write_access()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._ensure_write_access()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._ensure_write_access()
        return super().destroy(request, *args, **kwargs)


# --- Library Management ---

class LibraryViewSet(CachedListRetrieveMixin, ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated, IsSuperAdminForWrite]
    retrieve_cache_namespace = LIBRARY_CACHE_NAMESPACE

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_super_admin(self.request.user):
            return queryset

        actor_library = get_user_library(self.request.user)
        if not actor_library:
            return queryset.none()
        return queryset.filter(pk=actor_library.pk)

    def list(self, request, *args, **kwargs):
        return cache_api_response(
            LIBRARY_CACHE_NAMESPACE,
            request,
            lambda: self._list_uncached(request, *args, **kwargs),
        )

    def _list_uncached(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if is_super_admin(request.user):
            staffs = (
                User.objects.filter(role__in=["ADMIN", "SUPER ADMIN"])
                .order_by("first_name", "last_name")
            )
        else:
            actor_library = get_user_library(request.user)
            staffs = (
                User.objects.filter(role__in=["ADMIN", "SUPER ADMIN"], library=actor_library)
                .order_by("first_name", "last_name")
            )
        admin_staffs = [
            {
                "id": str(staff.id),
                "staff_id": str(staff.id),
                "user_id": str(staff.id),
                "name": f"{staff.first_name} {staff.last_name}".strip() or staff.id_number,
                "role": staff.role,
                "library_id": str(staff.library_id) if staff.library_id else None,
            }
            for staff in staffs
        ]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["libraries"] = serializer.data
            response.data["admin_staffs"] = admin_staffs
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({"libraries": serializer.data, "admin_staffs": admin_staffs}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()
        invalidate_library_caches()

    def perform_update(self, serializer):
        serializer.save()
        invalidate_library_caches()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_library_caches()


class LibraryPolicyViewSet(ModelViewSet):
    queryset = LibraryPolicy.objects.select_related("library").all()
    serializer_class = LibraryPolicySerializer
    permission_classes = [IsAuthenticated]

    def _ensure_write_access(self):
        if not is_admin_like(self.request.user):
            raise ValidationError("Only ADMIN or SUPER ADMIN can manage library policies.")

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_super_admin(self.request.user):
            return queryset

        actor_library = get_user_library(self.request.user)
        if not actor_library:
            return queryset.none()
        return queryset.filter(library=actor_library)

    def perform_create(self, serializer):
        self._ensure_write_access()
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self._ensure_write_access()
        serializer.save()
        return Response(serializer.data)

    partial_update = update

    def perform_destroy(self, instance):
        self._ensure_write_access()
        instance.delete()


# --- User Management ---

class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, CanCreateUsers]


class UserDeleteAPIView(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, CanDeleteUsers]

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_library_caches()


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="role",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter users by role. Example values: ADMIN, MEMBER, SUPER ADMIN",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Search by first name or id.",
        ),
    ]
)
class UserListAPIView(ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^first_name', '=id_number']

    def get_queryset(self):
        queryset = User.objects.all().order_by("first_name", "last_name", "id_number")
        role = self.request.query_params.get("role")
        search = self.request.query_params.get("search")
        actor = self.request.user
        actor_role = " ".join(
        normalize_role(getattr(actor, "role", "")).upper().split())
        
        if role:
            normalized_role = " ".join(role.upper().split())
            if normalized_role == "STACKSTAFF":
                normalized_role = "STACK STAFF"
            elif normalized_role == "TECHNICALSTAFF":
                normalized_role = "TECHNICAL STAFF"
            elif normalized_role == "FRONTDESKSTAFF":
                normalized_role = "FRONT DESK STAFF"
            elif normalized_role == "SUPERADMIN":
                normalized_role = "SUPER ADMIN"
            elif normalized_role == "DEPARTMENTHEAD":
                normalized_role = "DEPARTMENT HEAD"

            queryset = queryset.filter(role__iexact=normalized_role).order_by("first_name", "last_name", "id_number")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(id_number__icontains=search)
                | Q(email__icontains=search)
            )
        if actor_role != "SUPERADMIN":
            actor_library = get_user_library(actor)
            if actor_role == "ADMIN" or actor_role == "STACKSTAFF" or actor_role == "TECHNICALSTAFF" or actor_role == "FRONTDESKSTAFF":
                if actor_library:
                    queryset = queryset.filter(
                        Q(library=actor_library)
                        | Q(role__iexact="MEMBER", library__isnull=True)
                    )
                else:
                    queryset = queryset.filter(pk=actor.pk)
            elif actor_library:
                queryset = queryset.filter(library=actor_library)
            else:
                queryset = queryset.filter(pk=actor.pk)
        
        return queryset


class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin_like(request.user):
            return Response({"detail": "Only ADMIN or SUPER ADMIN can update users."}, status=status.HTTP_403_FORBIDDEN)

        if not is_super_admin(request.user):
            actor_library = get_user_library(request.user)
            target_role = normalize_role(getattr(user, "role", None))
            user_is_global_member = target_role == "MEMBER" and user.library_id is None
            if not actor_library or (user.library_id != actor_library.id and not user_is_global_member):
                return Response({"detail": "You can only update users in your library."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserListSerializer(user, context={"request": request}).data, status=status.HTTP_200_OK)


class AdminUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staffs = (
            User.objects.filter(role__in=["ADMIN"])
            .order_by("first_name", "last_name")
        )
        if not is_super_admin(request.user):
            actor_library = get_user_library(request.user)
            staffs = staffs.filter(Q(library=actor_library) | Q(library__isnull=True))
        data = [
            {
                "staff_id": str(staff.id),
                "name": f"{staff.first_name} {staff.last_name}".strip() or staff.id_number,
                "role": staff.role,
                "user_id": str(staff.id),
                "library_id": str(staff.library_id) if staff.library_id else None,
            }
            for staff in staffs
        ]
        return Response(data, status=status.HTTP_200_OK)


class UserMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user, context={"request": request}).data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserMeSerializer(request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.decorators import action

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(member_id=user).order_by('-sent_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.status = 'READ'
        notification.save()
        return Response({'status': 'notification marked as read'})
