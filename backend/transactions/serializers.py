from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from .models import Borrow, Reservation, Return, Circulation
from .services import calculate_overdue_days, finalize_return_for_borrow
from .services import notify_borrow_success, notify_return_success
from user_mgt.access import get_active_library_policy, get_user_library, is_super_admin, normalize_role, is_staff_like
from user_mgt.models import User

class ReservationSerializer(serializers.ModelSerializer):

    material_title = serializers.CharField(source="material_id.title", read_only=True)
    material_author = serializers.CharField(source="material_id.author", read_only=True)
    member_id_number = serializers.CharField(source="member.id_number", required=False)
    library_name = serializers.CharField(source="material_id.library.name", read_only=True)
    class Meta:
        model = Reservation
        fields = [
            "id",
            "member",
            "material_id",
            "reserve_date",
            "expiry_date",
            "status",
            "material_title",
            "material_author",
            "member_id_number",
            "library_name",
        ]

        read_only_fields = [
            "id",
            "member",
            "reserve_date",
            "expiry_date",
            "status",
            "material_title",
            "material_author",
        ]

    def validate(self, attrs):

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or normalize_role(getattr(user, "role", None)) != "MEMBER":
            raise serializers.ValidationError("Only members can reserve materials.")

        material = attrs.get("material_id")

        if not material:
            raise serializers.ValidationError({"material_id": "Material is required."})
        if not material.library_id:
            raise serializers.ValidationError({"material_id": "This material is not assigned to a library yet."})
        # Library restriction removed: Members can reserve materials from any library


        # If copies are available, user should borrow instead
        if material.available_copies > 0:
            raise serializers.ValidationError(
                {"material_id": "Material is available. Borrow instead."}
            )

        # Prevent duplicate reservation
        existing = Reservation.objects.filter(
            member=user,
            material_id=material,
            status="RESERVED",
            expiry_date__gt=timezone.now()
        ).exists()

        if existing:
            raise serializers.ValidationError(
                "You already reserved this material."
            )

        # Limit reservation queue
        total_reservations = Reservation.objects.filter(
            material_id=material,
            status="RESERVED",
            expiry_date__gt=timezone.now()
        ).count()

        if total_reservations >= material.total_copies:
            raise serializers.ValidationError(
                {"material_id": "Reservation queue is full."}
            )

        return attrs

    def create(self, validated_data):

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or normalize_role(getattr(user, "role", None)) != "MEMBER":
            raise serializers.ValidationError("Only members can create reservations.")

        validated_data["member"] = user
        policy = get_active_library_policy(material.library if (material := validated_data.get("material_id")) else None)

        validated_data["expiry_date"] = (
            timezone.now() + timezone.timedelta(hours=int(getattr(policy, "reservation_hold_hours", 24) or 24))
        )

        validated_data["status"] = "RESERVED"

        return super().create(validated_data)
    
class BorrowSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    member_id = serializers.CharField(source="member.id_number", read_only=True)
    material_title = serializers.CharField(source="material.title", read_only=True)
    material_author = serializers.CharField(source="material.author", read_only=True)
    member_name = serializers.CharField(source="member.first_name", read_only=True)
    estimated_fine_amount = serializers.SerializerMethodField()
    is_returned = serializers.SerializerMethodField()
    return_id = serializers.SerializerMethodField()
    returned_at = serializers.SerializerMethodField()
    final_fine_amount = serializers.SerializerMethodField()
    library_name = serializers.CharField(source="material.library.name", read_only=True)

    class Meta:
        model = Borrow
        fields = [
            "id",
            "member",
            "member_id",
            "material",
            "reservation",
            "borrow_date",
            "due_date",
            "estimated_fine_amount",
            "status",
            "created_by",
            "material_title",
            "member_name",
            "material_author",
            "library_name",
            "is_returned",
            "return_id",
            "returned_at",
            "final_fine_amount",
        ]
        extra_kwargs = {
            "member": {"required": False},
            "material": {"required": False},
        }

        read_only_fields = [
            "id",
            "borrow_date",
            "status",
            "created_by",
            "material_title",
            "material_author",
            "member_name",
            "due_date",
        ]

    def get_is_returned(self, obj):
        return obj.status == "RETURNED"

    def get_return_id(self, obj):
        latest_return = obj.returns.order_by("-return_date").first()
        return latest_return.id if latest_return else None

    def get_returned_at(self, obj):
        if obj.status != "RETURNED":
            return None
        latest_return = obj.returns.order_by("-return_date").first()
        return latest_return.return_date if latest_return else None

    def get_final_fine_amount(self, obj):
        latest_return = obj.returns.order_by("-return_date").first()
        return latest_return.fine_amount if latest_return else None

    def get_estimated_fine_amount(self, obj):
        latest_return = obj.returns.order_by("-return_date").first()
        if latest_return:
            return latest_return.fine_amount

        policy = get_active_library_policy(getattr(obj.material, "library", None))
        grace_period_days = int(getattr(policy, "grace_period_days", 0) or 0)
        overdue_days = calculate_overdue_days(obj.due_date, grace_period_days=grace_period_days)
        daily_fine_rate = Decimal(str(getattr(policy, "overdue_daily_rate", getattr(settings, "LIBRARY_DAILY_FINE_RATE", "0"))))
        return daily_fine_rate * overdue_days

    def validate(self, attrs):
        reservation = attrs.get("reservation")

        # 2. Handle Reservation logic (Overrides member/material)
        if reservation:
            if reservation.status != "RESERVED" or reservation.expiry_date <= timezone.now():
                raise serializers.ValidationError({"reservation": "Reservation is inactive or expired."})
            attrs["member"] = reservation.member
            attrs["material"] = reservation.material_id

        # 3. Final Check on the resolved member
        final_member = attrs.get("member")
        if not final_member:
            raise serializers.ValidationError({"member": "Member is required."})

        # The Logic Gate: Check the role string
        # We use .strip() and .upper() to ensure minor typos don't break it
        user_role = normalize_role(getattr(final_member, "role", ""))
        
        if user_role != "MEMBER":
            raise serializers.ValidationError({
                "member": f"Validation failed. User role is '{getattr(final_member, 'role', 'N/A')}', but 'MEMBER' is required."
            })

        # 4. Material Availability
        material = attrs.get("material")
        if not material:
            raise serializers.ValidationError({"material": "Material is required."})
        if not material.can_borrow:
            raise serializers.ValidationError({"material": "This material cannot be borrowed."})
        if not material.library_id:
            raise serializers.ValidationError({"material": "This material is not assigned to a library yet."})
        # Library restriction removed: Members can borrow materials from any library

        # Restrict Borrow: Allowed only for materials located in the STACK
        if getattr(material, "location", "") != "STACK":
            raise serializers.ValidationError({"material": "Borrow is only allowed for materials located in the STACK."})

        policy = get_active_library_policy(getattr(material, "library", None))
        max_active_borrows = int(getattr(policy, "max_active_borrows", 3) or 3)
        active_count = Borrow.objects.filter(member=final_member).exclude(status="RETURNED").count()
        if active_count >= max_active_borrows:
            raise serializers.ValidationError({"member": f"This member has already reached the maximum active borrow limit of {max_active_borrows}."})

        # Do not trust cached available_copies alone; compute effective availability.
        active_borrows = Borrow.objects.filter(material=material).exclude(status="RETURNED").count()
        effective_available = material.total_copies - active_borrows
        if effective_available <= 0:
            raise serializers.ValidationError({"material": "No available copies to borrow."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = normalize_role(getattr(user, "role", None))
        if role != "STACKSTAFF":
            raise serializers.ValidationError("Only STACK STAFF can create borrows.")
        material = validated_data["material"]
        reservation = validated_data.get("reservation")
        policy = get_active_library_policy(getattr(material, "library", None))
        borrow_duration_days = int(getattr(policy, "borrow_duration_days", 7) or 7)

        with transaction.atomic():
            locked_material = material.__class__.objects.select_for_update().get(pk=material.pk)
            currently_borrowed = Borrow.objects.filter(
                material=locked_material,
            ).exclude(status="RETURNED").count()
            available_after_borrow = locked_material.total_copies - (currently_borrowed + 1)

            if available_after_borrow < 0:
                raise serializers.ValidationError({"material": "No available copies to borrow."})

            locked_material.available_copies = available_after_borrow
            locked_material.save(update_fields=["available_copies"])

            # set due date (example: 7 days)
            validated_data["material"] = locked_material
            validated_data["due_date"] = timezone.now() + timezone.timedelta(days=borrow_duration_days)
            validated_data["created_by"] = user

            # if borrowed from reservation, expire reservation
            if reservation:
                reservation.status = "EXPIRED"
                reservation.save(update_fields=["status"])

            borrow = super().create(validated_data)
            transaction.on_commit(lambda: notify_borrow_success(borrow))
            return borrow


class ReturnSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(source="borrow.member", read_only=True)
    material = serializers.PrimaryKeyRelatedField(source="borrow.material", read_only=True)
    member_name = serializers.CharField(source="borrow.member.first_name", read_only=True)
    material_title = serializers.CharField(source="borrow.material.title", read_only=True)
    due_date = serializers.DateTimeField(source="borrow.due_date", read_only=True)
    payment_status = serializers.SerializerMethodField()
    payment_reference = serializers.SerializerMethodField()
    settlement_status = serializers.SerializerMethodField()
    requires_payment = serializers.SerializerMethodField()
    library_name = serializers.CharField(source="borrow.material.library.name", read_only=True)

    class Meta:
        model = Return
        fields = [
            "id",
            "borrow",
            "member",
            "member_name",
            "material",
            "material_title",
            "due_date",
            "return_date",
            "fine_amount",
            "created_by",
            "payment_status",
            "payment_reference",
            "settlement_status",
            "requires_payment",
            "library_name",
        ]
        read_only_fields = [
            "id",
            "member",
            "member_name",
            "material",
            "material_title",
            "due_date",
            "return_date",
            "fine_amount",
            "created_by",
            "payment_status",
            "payment_reference",
        ]

    def _latest_payment(self, obj):
        return obj.payment.order_by("-payment_date").first()

    def get_payment_status(self, obj):
        latest_payment = self._latest_payment(obj)
        return latest_payment.status if latest_payment else "UNPAID"

    def get_payment_reference(self, obj):
        latest_payment = self._latest_payment(obj)
        return latest_payment.transaction_reference if latest_payment else None

    def get_requires_payment(self, obj):
        return Decimal(str(obj.fine_amount or 0)) > 0

    def get_settlement_status(self, obj):
        if Decimal(str(obj.fine_amount or 0)) <= 0:
            return "COMPLETED"
        payment_status = self.get_payment_status(obj)
        return "COMPLETED" if payment_status == "COMPLETED" else "AWAITING_PAYMENT"

    def validate(self, attrs):
        borrow = attrs.get("borrow")
        if not borrow:
            raise serializers.ValidationError({"borrow": "Borrow is required."})

        if borrow.returns.exists():
            raise serializers.ValidationError({"borrow": "This borrow has already been returned."})
        if not getattr(getattr(borrow, "material", None), "library_id", None):
            raise serializers.ValidationError({"borrow": "This borrowed material is not assigned to a library yet."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not is_staff_like(user):
            raise serializers.ValidationError("Only library staff can record returns.")

        borrow = validated_data["borrow"]
        now = timezone.now()
        policy = get_active_library_policy(getattr(borrow.material, "library", None))
        grace_period_days = int(getattr(policy, "grace_period_days", 0) or 0)

        overdue_days = calculate_overdue_days(borrow.due_date, now=now, grace_period_days=grace_period_days)
        daily_fine_rate = Decimal(str(getattr(policy, "overdue_daily_rate", getattr(settings, "LIBRARY_DAILY_FINE_RATE", "0"))))
        validated_data["fine_amount"] = daily_fine_rate * overdue_days
        validated_data["created_by"] = user

        return_record = super().create(validated_data)

        # Finalize immediately only when no fine is due.
        # If fine exists, payment verification will finalize the return.
        if return_record.fine_amount <= 0:
            finalize_return_for_borrow(borrow)

        transaction.on_commit(lambda: notify_return_success(borrow, return_record))
        return return_record


class BorrowUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ["due_date", "status"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or normalize_role(getattr(user, "role", None)) not in ["STACKSTAFF", "TECHNICALSTAFF", "FRONTDESKSTAFF", "ADMIN", "SUPERADMIN"]:
            raise serializers.ValidationError("Only staff-role users can update borrows.")
        
        status_val = attrs.get("status")
        if status_val and status_val not in ["BORROWED", "OVERDUE", "RETURNED"]:
            raise serializers.ValidationError({"status": "Invalid status."})
            
        return attrs


class ReservationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["expiry_date", "status"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or normalize_role(getattr(user, "role", None)) not in ["STACKSTAFF", "TECHNICALSTAFF", "FRONTDESKSTAFF", "ADMIN", "SUPERADMIN"]:
            raise serializers.ValidationError("Only staff-role users can update reservations.")
            
        status_val = attrs.get("status")
        if status_val and status_val not in ["RESERVED", "EXPIRED", "CANCELLED"]:
            raise serializers.ValidationError({"status": "Invalid status."})
            
        return attrs


class CirculationSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    member_id = serializers.CharField(source="member.id_number", read_only=True)
    material_title = serializers.CharField(source="material.title", read_only=True)
    material_author = serializers.CharField(source="material.author", read_only=True)
    member_name = serializers.CharField(source="member.first_name", read_only=True)
    library_name = serializers.CharField(source="material.library.name", read_only=True)

    class Meta:
        model = Circulation
        fields = [
            "id",
            "member",
            "member_id",
            "material",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "material_title",
            "member_name",
            "material_author",
            "library_name",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "material_title",
            "material_author",
            "member_name",
        ]

    def validate(self, attrs):
        material = attrs.get("material")
        if not material:
            raise serializers.ValidationError({"material": "Material is required."})
        if getattr(material, "location", "") != "SHELF":
            raise serializers.ValidationError({"material": "Circulation is only allowed for materials located on the SHELF."})
        
        # Do not trust cached available_copies alone; compute effective availability.
        active_circs = Circulation.objects.filter(material=material, status="BORROWED").count()
        effective_available = material.total_copies - active_circs
        if effective_available <= 0:
            raise serializers.ValidationError({"material": "No available copies to circulate."})
        
        # Check maximum active circulations or duplicate circulation
        final_member = attrs.get("member")
        user_role = normalize_role(getattr(final_member, "role", ""))
        if user_role != "MEMBER":
            raise serializers.ValidationError({"member": "Circulation is only for members."})
        
        # Prevent duplicate active circulation of same book
        existing = Circulation.objects.filter(member=final_member, material=material, status="BORROWED").exists()
        if existing:
            raise serializers.ValidationError("This member already has an active circulation for this material.")
        
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = normalize_role(getattr(user, "role", None))
        if role != normalize_role("FRONT DESK STAFF"):
            raise serializers.ValidationError("Only FRONT DESK STAFF can create circulations.")
        
        material = validated_data["material"]
        with transaction.atomic():
            locked_material = material.__class__.objects.select_for_update().get(pk=material.pk)
            active_circs = Circulation.objects.filter(material=locked_material, status="BORROWED").count()
            effective_available = locked_material.total_copies - active_circs
            if effective_available <= 0:
                raise serializers.ValidationError({"material": "No available copies to circulate."})
            
            # Decrease available_copies
            locked_material.available_copies = effective_available - 1
            locked_material.save(update_fields=["available_copies"])
            
            validated_data["material"] = locked_material
            validated_data["created_by"] = user
            validated_data["status"] = "BORROWED"
            
            return super().create(validated_data)


