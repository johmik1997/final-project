
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from django.http import HttpResponse
from material_mgt.cache import invalidate_material_caches
from material_mgt.models import *
from user_mgt.access import get_user_library, is_super_admin, normalize_role
from .serializers import *
from .services import (
    sync_overdue_borrow_statuses,
    notify_circulation_borrow_success,
    notify_circulation_return_success,
)
from user_mgt.permissions import *
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None
# Create your views here.

class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.select_related("member__library", "material_id__library").all()
    serializer_class = ReservationSerializer
    # permission_classes = [IsAuthenticated]

    def _expire_overdue(self, qs):
        now = timezone.now()
        qs.filter(status="RESERVED", expiry_date__lt=now).update(status="EXPIRED")
        return qs

    def get_queryset(self):
        user = self.request.user
        base_qs = Reservation.objects.select_related("member__library", "material_id__library").all()
        self._expire_overdue(base_qs)
        if normalize_role(getattr(user, "role", None)) == "MEMBER":
            return base_qs.filter(member=user)
        if not is_super_admin(user):
            actor_library = get_user_library(user)
            if not actor_library:
                return base_qs.none()
            return base_qs.filter(material_id__library=actor_library)
        return base_qs

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ReservationUpdateSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        user_role = normalize_role(getattr(request.user, "role", None))
        
        # Only owner (member) or staff can cancel
        if user_role == "MEMBER" and reservation.member != request.user:
            return Response({"detail": "You cannot cancel other members' reservations."}, status=status.HTTP_403_FORBIDDEN)
            
        if reservation.status != "CANCELLED":
            reservation.status = "CANCELLED"
            reservation.save(update_fields=["status"])
        return Response(status=204)
class BorrowViewSet(ModelViewSet):
    
    queryset = Borrow.objects.select_related("member__library", "material__library", "created_by").all().order_by("-borrow_date")
    serializer_class = BorrowSerializer
    permission_classes = [IsStackStaffForWrite]

    def get_queryset(self):
        sync_overdue_borrow_statuses()
        queryset = Borrow.objects.select_related("member__library", "material__library", "created_by").all().order_by("-borrow_date")
        user = self.request.user
        if normalize_role(getattr(user, "role", None)) == "MEMBER":
            return queryset.filter(member=user)
        if not is_super_admin(user):
            actor_library = get_user_library(user)
            if not actor_library:
                return queryset.none()
            return queryset.filter(material__library=actor_library)
        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return BorrowUpdateSerializer
        return BorrowSerializer

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        borrow = self.get_object()
        user_role = normalize_role(getattr(request.user, "role", None))
        
        if user_role not in ["STACKSTAFF", "TECHNICALSTAFF", "FRONTDESKSTAFF", "ADMIN", "SUPERADMIN"]:
            return Response({"detail": "Only staff-role users can delete borrows."}, status=status.HTTP_403_FORBIDDEN)
            
        if borrow.status != "RETURNED":
            material = borrow.material
            if material:
                material.available_copies = min(material.total_copies, (material.available_copies or 0) + 1)
                material.save(update_fields=["available_copies"])
        borrow.delete()
        invalidate_material_caches()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        borrow = self.get_object()
        if fitz is None:
            return Response({"detail": "PyMuPDF is not installed. Install it with: pip install PyMuPDF"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        doc = fitz.open()
        page = doc.new_page()
        
        y = 50
        page.insert_text(fitz.Point(50, y), "Library Borrow Receipt", fontsize=20)
        y += 40
        page.insert_text(fitz.Point(50, y), f"Material: {borrow.material.title if borrow.material else 'Unknown'}", fontsize=12)
        y += 20
        page.insert_text(fitz.Point(50, y), f"Member: {borrow.member.get_full_name() if borrow.member else 'Unknown'} ({borrow.member.id_number if borrow.member else ''})", fontsize=12)
        y += 20
        page.insert_text(fitz.Point(50, y), f"Borrowed At: {borrow.borrow_date.strftime('%Y-%m-%d %H:%M')}", fontsize=12)
        y += 20
        page.insert_text(fitz.Point(50, y), f"Due Date: {borrow.due_date.strftime('%Y-%m-%d %H:%M')}", fontsize=12)
        y += 40
        page.insert_text(fitz.Point(50, y), "Thank you for using our library!", fontsize=12)
        
        pdf_bytes = doc.write()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{borrow.id}.pdf"'
        return response


    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        sync_overdue_borrow_statuses()
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset = Borrow.objects.select_related("member__library", "material__library", "created_by").filter(member=user).order_by("-borrow_date")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReturnViewSet(ModelViewSet):

    queryset = Return.objects.select_related("borrow__member__library", "borrow__material__library", "created_by").all().order_by("-return_date")
    serializer_class = ReturnSerializer
    # permission_classes = [IsStackStaffForWrite]

    def get_queryset(self):
        user = self.request.user
        base_qs = Return.objects.select_related("borrow__member__library", "borrow__material__library", "created_by").all().order_by("-return_date")
        if normalize_role(getattr(user, "role", None)) == "MEMBER":
            return base_qs.filter(borrow__member=user)
        if not is_super_admin(user):
            actor_library = get_user_library(user)
            if not actor_library:
                return base_qs.none()
            return base_qs.filter(borrow__material__library=actor_library)
        return base_qs

    def perform_create(self, serializer):
        serializer.save()


class IsFrontDeskStaffForWrite(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        role = normalize_role(getattr(user, "role", None))
        return role == normalize_role("FRONT DESK STAFF")


class CirculationViewSet(ModelViewSet):
    queryset = Circulation.objects.select_related("member__library", "material__library", "created_by").all().order_by("-created_at")
    serializer_class = CirculationSerializer
    permission_classes = [IsFrontDeskStaffForWrite]

    def get_queryset(self):
        queryset = Circulation.objects.select_related("member__library", "material__library", "created_by").all().order_by("-created_at")
        user = self.request.user
        if normalize_role(getattr(user, "role", None)) == "MEMBER":
            return queryset.filter(member=user)
        if not is_super_admin(user):
            actor_library = get_user_library(user)
            if not actor_library:
                return queryset.none()
            return queryset.filter(material__library=actor_library)
        return queryset

    def perform_create(self, serializer):
        circulation = serializer.save()
        from django.db import transaction
        transaction.on_commit(lambda: notify_circulation_borrow_success(circulation))

    @action(detail=True, methods=["post"])
    def return_material(self, request, pk=None):
        circulation = self.get_object()
        if circulation.status == "RETURNED":
            return Response({"error": "Already returned."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            circulation.status = "RETURNED"
            circulation.save(update_fields=["status"])
            
            # Increment available copies
            material = circulation.material
            material.available_copies += 1
            material.save(update_fields=["available_copies"])
            
        from django.db import transaction as db_transaction
        db_transaction.on_commit(lambda: notify_circulation_return_success(circulation))
        db_transaction.on_commit(invalidate_material_caches)
        return Response({"success": True, "message": "Material returned successfully."})
