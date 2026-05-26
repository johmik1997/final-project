import secrets
import time
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from material_mgt.cache import invalidate_library_caches
from transactions.models import Borrow, Reservation
from .access import get_user_library, is_super_admin, normalize_role
from .member_access import validate_campus_student_registration, validate_member_account
from .email_utils import send_templated_user_email, send_templated_user_email_background
from .models import CampusStudent, Library, LibraryPolicy, Notification, User

# --- Helper Functions ---


def _get_user_profile(user):
    return user


def _build_media_url(request, file_field):
    if not file_field:
        return None
    url = file_field.url
    return request.build_absolute_uri(url) if request else url


def _password_reset_otp_cache_key(email):
    return f"password_reset_otp:{email.lower()}"


def _password_reset_confirm_cache_key(email, confirm_token):
    return f"password_reset_confirm:{email.lower()}:{confirm_token}"


def _validate_password_reset_otp(email, otp):
    now_ts = int(time.time())
    cache_key = _password_reset_otp_cache_key(email)
    otp_data = cache.get(cache_key)
    
    if not otp_data:
        raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

    expires_at = int(otp_data.get("expires_at", 0))
    if now_ts > expires_at:
        cache.delete(cache_key)
        raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

    expected_otp = str(otp_data.get("otp", ""))
    attempts = int(otp_data.get("attempts", 0))
    max_attempts = int(getattr(settings, "PASSWORD_RESET_OTP_MAX_ATTEMPTS", 5))

    if otp != expected_otp:
        attempts += 1
        if attempts >= max_attempts:
            cache.delete(cache_key)
            raise serializers.ValidationError({"otp": "Too many failed attempts. Request a new OTP."})
        else:
            otp_data["attempts"] = attempts
            remaining = max(1, expires_at - now_ts)
            cache.set(cache_key, otp_data, timeout=remaining)
        raise serializers.ValidationError({"otp": "Invalid OTP code."})

    return cache_key, otp_data


# --- Model Serializers ---

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ["id", "name", "campus", "location", "phone"]


class LibraryPolicySerializer(serializers.ModelSerializer):
    library_name = serializers.CharField(source="library.name", read_only=True)

    class Meta:
        model = LibraryPolicy
        fields = [
            "id",
            "library",
            "library_name",
            "name",
            "is_active",
            "borrow_duration_days",
            "max_active_borrows",
            "reservation_hold_hours",
            "overdue_daily_rate",
            "fair_condition_penalty_percent",
            "damaged_condition_penalty_percent",
            "lost_condition_penalty_percent",
            "grace_period_days",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "library_name", "created_at", "updated_at"]

    def validate_library(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if value is None and not is_super_admin(user):
            raise serializers.ValidationError("A library is required for non-super-admin users.")

        actor_library = get_user_library(user)
        if value is not None and not is_super_admin(user) and actor_library and value != actor_library:
            raise serializers.ValidationError("You can only manage policies for your assigned library.")

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if self.instance is None and not attrs.get("library") and not is_super_admin(user):
            actor_library = get_user_library(user)
            if actor_library:
                attrs["library"] = actor_library

        target_library = attrs.get("library")
        if target_library is None and self.instance is not None:
            target_library = self.instance.library

        if target_library is None:
            existing_global_policy = LibraryPolicy.objects.filter(library__isnull=True)
            if self.instance is not None:
                existing_global_policy = existing_global_policy.exclude(pk=self.instance.pk)

            if existing_global_policy.exists():
                raise serializers.ValidationError(
                    "Only one global library policy is allowed. Update the existing global policy instead."
                )

        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(write_only=True, required=True, max_length=15)
    department = serializers.CharField(write_only=True, required=False, max_length=70)
    user_type = serializers.ChoiceField(write_only=True, required=False, choices=[c[0] for c in User.USER_TYPE])
    library = serializers.PrimaryKeyRelatedField(
        queryset=Library.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "id_number",
            "first_name",
            "last_name",
            "email",
            "role",
            "status",
            "library",
            "password",
            "phone",
            "department",
            "user_type",
            "id_expiry_date",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context.get("request")
        creator = getattr(request, "user", None)
        target_role = attrs.get("role")
        creator_role = normalize_role(getattr(creator, "role", None))
        target_role_norm = normalize_role(target_role)
        actor_library = get_user_library(creator)
        chosen_library = attrs.get("library")

        if creator_role == "ADMIN" and target_role_norm in {"ADMIN", "SUPERADMIN"}:
            raise serializers.ValidationError("ADMIN users cannot create ADMIN or SUPER ADMIN accounts.")
        if creator_role not in {"ADMIN", "SUPERADMIN"}:
            raise serializers.ValidationError("Only ADMIN or SUPER ADMIN can create users.")
        if target_role_norm == "MEMBER":
            attrs["library"] = None
            chosen_library = None
        if creator_role != "SUPERADMIN":
            if not actor_library:
                raise serializers.ValidationError("Your account is not assigned to a library yet.")
            if target_role_norm not in {"MEMBER", "SUPERADMIN"}:
                attrs["library"] = actor_library
        else:
            staff_roles_requiring_library = {
                "STACKSTAFF",
                "TECHNICALSTAFF",
                "FRONTDESKSTAFF",
                "ADMIN",
                "DEPARTMENTHEAD",
            }
            if target_role_norm in staff_roles_requiring_library and not chosen_library:
                raise serializers.ValidationError({"library": "Library is required for this role."})
        if target_role_norm == "MEMBER":
            if not attrs.get("department"):
                raise serializers.ValidationError({"department": "Department is required for MEMBER."})
            if not attrs.get("user_type"):
                raise serializers.ValidationError({"user_type": "User type is required for MEMBER."})
        return attrs

    def _send_account_created_email(self, user, password):
        email = (user.email or "").strip()
        if not email:
            return
        login_url = getattr(settings, "FRONTEND_LOGIN_URL", "http://localhost:5173/login")
        send_templated_user_email_background(
            template_base="account_created",
            context={
                "first_name": user.first_name or user.id_number,
                "id_number": user.id_number,
                "email": email,
                "password": password,
                "login_url": login_url,
            },
            recipients=[email],
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        phone = validated_data.pop("phone")
        department = validated_data.pop("department", "UNASSIGNED")
        user_type = validated_data.pop("user_type", None)
        role_norm = normalize_role(validated_data.get("role"))
        if role_norm == "MEMBER":
            validated_data["library"] = None
        
        with transaction.atomic():
            if role_norm == "SUPERADMIN":
                user = User.objects.create_superuser(password=password, **validated_data)
            else:
                validated_data.setdefault("is_staff", role_norm == "ADMIN")
                user = User.objects.create_user(password=password, **validated_data)

            if role_norm == "MEMBER":
                user.department = department
                user.user_type = user_type
                campus = CampusStudent.objects.filter(id_number__iexact=user.id_number).first()
                if campus and campus.id_expiry_date and not user.id_expiry_date:
                    user.id_expiry_date = campus.id_expiry_date
            elif role_norm == "DEPARTMENTHEAD":
                user.department = department
            user.phone = phone
            user.must_change_password = True
            user.save()

        self._send_account_created_email(user, password)
        invalidate_library_caches()
        return user


# --- Authentication & Password Reset Serializers ---

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)


class FirstLoginChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})
        if not getattr(user, "must_change_password", False):
            raise serializers.ValidationError({"detail": "Password change is not required for this account."})

        validate_password(attrs["password"], user)
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password"])
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data["email"].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return

        ttl_seconds = int(getattr(settings, "PASSWORD_RESET_OTP_TTL_SECONDS", 600))
        resend_limit = int(getattr(settings, "PASSWORD_RESET_OTP_RESEND_SECONDS", 60))
        now_ts = int(time.time())
        cache_key = _password_reset_otp_cache_key(email)
        cached_data = cache.get(cache_key) or {}

        if cached_data.get("last_sent") and (now_ts - cached_data["last_sent"]) < resend_limit:
            wait = resend_limit - (now_ts - cached_data["last_sent"])
            raise serializers.ValidationError({"detail": f"Please wait {wait}s before requesting another OTP."})

        otp = f"{secrets.randbelow(1_000_000):06d}"
        cache.set(cache_key, {"otp": otp, "attempts": 0, "expires_at": now_ts + ttl_seconds, "last_sent": now_ts}, timeout=ttl_seconds + 60)

        send_templated_user_email(
            template_base="password_reset_otp",
            context={
                "otp": otp,
                "expiry_minutes": max(1, ttl_seconds // 60),
            },
            recipients=[user.email],
        )


class ConfirmResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        _validate_password_reset_otp(email, attrs["otp"].strip())
        attrs["email"] = email
        return attrs

    def save(self):
        email = self.validated_data["email"]
        ttl = int(getattr(settings, "PASSWORD_RESET_CONFIRM_TTL_SECONDS", 600))
        confirm_token = secrets.token_urlsafe(24)
        cache.set(_password_reset_confirm_cache_key(email, confirm_token), True, timeout=ttl)
        return {"confirm_token": confirm_token, "expires_in": ttl}


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirm_token = serializers.CharField(write_only=True, required=False, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        email = attrs["email"].strip().lower()
        request = self.context.get("request")
        confirm_token = attrs.get("confirm_token")
        if confirm_token:
            confirm_token = confirm_token.strip()
        if not confirm_token and request:
            confirm_token = request.COOKIES.get("password_reset_confirm_token")

        if not confirm_token or not cache.get(_password_reset_confirm_cache_key(email, confirm_token)):
            raise serializers.ValidationError({"detail": "Confirmation session expired. Please verify OTP again."})

        try:
            attrs["user"] = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid request."})

        attrs["_confirm_cache_key"] = _password_reset_confirm_cache_key(email, confirm_token)
        attrs["_otp_cache_key"] = _password_reset_otp_cache_key(email)
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        cache.delete(self.validated_data["_confirm_cache_key"])
        cache.delete(self.validated_data["_otp_cache_key"])
        return user


# --- User & Profile Serializers ---

class UserMeSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    library_id = serializers.UUIDField(source="library.id", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "id_number",
            "first_name",
            "last_name",
            "email",
            "role",
            "status",
            "id_expiry_date",
            "must_change_password",
            "library_id",
            "library_name",
            "phone",
            "photo",
        ]
        read_only_fields = [
            "id",
            "id_number",
            "role",
            "status",
            "id_expiry_date",
            "must_change_password",
            "library_id",
            "library_name",
            "phone",
            "photo",
        ]

    def get_phone(self, obj):
        profile = _get_user_profile(obj)
        return getattr(profile, "phone", None)

    def get_photo(self, obj):
        profile = _get_user_profile(obj)
        return _build_media_url(self.context.get("request"), getattr(profile, "photo", None))


class UserListSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="id", read_only=True)
    phone = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    library_id = serializers.UUIDField(source="library.id", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "user_id", "id_number", "first_name", "last_name", "email", "role", "status", "library_id", "library_name", "phone", "photo"]

    def get_phone(self, obj):
        profile = _get_user_profile(obj)
        return getattr(profile, "phone", None)

    def get_photo(self, obj):
        profile = _get_user_profile(obj)
        return _build_media_url(self.context.get("request"), getattr(profile, "photo", None))


class StudentSelfRegisterSerializer(serializers.Serializer):
    id_number = serializers.CharField(max_length=30)
    full_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        campus = validate_campus_student_registration(
            id_number=attrs["id_number"],
            full_name=attrs["full_name"],
            phone=attrs.get("phone") or "",
            email=attrs.get("email") or "",
        )
        attrs["campus_record"] = campus
        return attrs

    def create(self, validated_data):
        campus = validated_data["campus_record"]
        password = validated_data["password"]
        full_name = str(validated_data["full_name"]).strip()
        parts = full_name.split(None, 1)
        first_name = parts[0] if parts else full_name
        last_name = parts[1] if len(parts) > 1 else ""

        with transaction.atomic():
            user = User.objects.create_user(
                id_number=str(validated_data["id_number"]).strip(),
                password=password,
                email=validated_data["email"].strip().lower(),
                first_name=first_name,
                last_name=last_name,
                role="MEMBER",
                status="ACTIVE",
                user_type="STUDENT",
                department=(campus.department or "UNASSIGNED").strip() or "UNASSIGNED",
                phone=str(validated_data.get("phone") or campus.phone or "").strip(),
                library=None,
                id_expiry_date=campus.id_expiry_date,
                must_change_password=False,
            )
        email = (user.email or "").strip()
        if email:
            login_url = getattr(settings, "FRONTEND_LOGIN_URL", "http://localhost:5173/login")
            send_templated_user_email_background(
                template_base="account_created",
                context={
                    "first_name": user.first_name or user.id_number,
                    "id_number": user.id_number,
                    "email": email,
                    "password": "(the password you chose during registration)",
                    "login_url": login_url,
                },
                recipients=[email],
            )
        invalidate_library_caches()
        return user


class CampusStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusStudent
        fields = [
            "id",
            "id_number",
            "full_name",
            "phone",
            "department",
            "campus",
            "status",
            "id_expiry_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        member_error = validate_member_account(self.user, context="login")
        if member_error:
            raise serializers.ValidationError({"detail": member_error})
        if str(getattr(self.user, "status", "")).strip().upper() != "ACTIVE":
            raise serializers.ValidationError({"detail": "Student is inactive."})
        profile = _get_user_profile(self.user)
        data["user"] = {
            "id": str(self.user.id),
            "id_number": self.user.id_number,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "role": self.user.role,
            "status": self.user.status,
            "must_change_password": bool(getattr(self.user, "must_change_password", False)),
            "library_id": str(self.user.library_id) if self.user.library_id else None,
            "library_name": self.user.library.name if self.user.library_id else None,
            "phone": getattr(profile, "phone", None),
            "photo": _build_media_url(self.context.get("request"), getattr(profile, "photo", None)),
            "id_expiry_date": (
                self.user.id_expiry_date.isoformat() if getattr(self.user, "id_expiry_date", None) else None
            ),
        }
        data["must_change_password"] = bool(getattr(self.user, "must_change_password", False))
        return data


class AdminUserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    staff_id = serializers.SerializerMethodField()
    library_id = serializers.UUIDField(source="library.id", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.id_number

    def get_staff_id(self, obj):
        return str(obj.id)

    class Meta:
        model = User
        fields = ["id", "staff_id", "id_number", "name", "first_name", "last_name", "email", "role", "status", "library_id", "library_name"]


class UserUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=15)
    department = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=70)
    user_type = serializers.ChoiceField(write_only=True, required=False, choices=[c[0] for c in User.USER_TYPE])
    library = serializers.PrimaryKeyRelatedField(
        queryset=Library.objects.all(),
        required=False,
        allow_null=True,
    )
    library_id = serializers.UUIDField(source="library.id", read_only=True)
    library_name = serializers.CharField(source="library.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "id_number",
            "first_name",
            "last_name",
            "email",
            "role",
            "status",
            "library",
            "library_id",
            "library_name",
            "phone",
            "department",
            "user_type",
            "id_expiry_date",
        ]
        read_only_fields = ["id", "library_id", "library_name"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        actor = getattr(request, "user", None)
        actor_role = normalize_role(getattr(actor, "role", None))
        target_role = normalize_role(attrs.get("role", self.instance.role))
        actor_library = get_user_library(actor)
        chosen_library = attrs.get("library", self.instance.library)

        if actor_role not in {"ADMIN", "SUPERADMIN"}:
            raise serializers.ValidationError("Only ADMIN or SUPER ADMIN can update users.")

        if actor_role == "ADMIN":
            if target_role in {"ADMIN", "SUPERADMIN"}:
                raise serializers.ValidationError("ADMIN users cannot promote users to ADMIN or SUPER ADMIN.")
            if not actor_library:
                raise serializers.ValidationError("Your account is not assigned to a library yet.")
            if target_role not in {"MEMBER", "SUPERADMIN"}:
                attrs["library"] = actor_library
                chosen_library = actor_library
        elif target_role not in {"MEMBER", "SUPERADMIN"} and not chosen_library:
            raise serializers.ValidationError({"library": "Library is required for this role."})

        if target_role == "MEMBER":
            attrs["library"] = None
            if not (attrs.get("department") or getattr(self.instance, "department", None)):
                raise serializers.ValidationError({"department": "Department is required for MEMBER."})
            if not (attrs.get("user_type") or getattr(self.instance, "user_type", None)):
                raise serializers.ValidationError({"user_type": "User type is required for MEMBER."})

        return attrs

    def update(self, instance, validated_data):
        phone = validated_data.pop("phone", None)
        department = validated_data.pop("department", None)
        user_type = validated_data.pop("user_type", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if phone is not None:
            instance.phone = phone
        if department is not None:
            instance.department = department
        if user_type is not None:
            instance.user_type = user_type
        instance.save()

        invalidate_library_caches()
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
