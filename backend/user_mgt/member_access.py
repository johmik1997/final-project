"""Shared checks for member accounts (login, borrow, register)."""

from django.utils import timezone

from .access import normalize_role
from .models import CampusStudent, User


def normalize_person_name(value: str) -> str:
    return " ".join(str(value or "").strip().upper().split())


def names_match(entered: str, expected: str) -> bool:
    entered_norm = normalize_person_name(entered)
    expected_norm = normalize_person_name(expected)
    if not entered_norm or not expected_norm:
        return False
    return entered_norm == expected_norm


def is_id_expired(expiry_date, on_date=None):
    if not expiry_date:
        return False
    today = on_date or timezone.localdate()
    return expiry_date < today


def get_member_id_expiry(user: User):
    if getattr(user, "id_expiry_date", None):
        return user.id_expiry_date
    if normalize_role(getattr(user, "role", "")) != "MEMBER":
        return None
    if getattr(user, "user_type", "") != "STUDENT":
        return None
    campus = CampusStudent.objects.filter(id_number=user.id_number).only("id_expiry_date").first()
    return campus.id_expiry_date if campus else None


def validate_member_account(user: User, *, context: str = "access"):
    """
    Return an error message string when the member cannot proceed, else None.
    context: login | borrow | register
    """
    role_norm = normalize_role(getattr(user, "role", ""))
    if role_norm != "MEMBER":
        return None

    status = str(getattr(user, "status", "") or "").strip().upper()
    if status != "ACTIVE":
        if status == "INACTIVE":
            return "Student is inactive."
        if status == "SUSPENDED":
            return "Your account is suspended."
        if status == "DEACTIVATED":
            return "Your account is deactivated."
        return "Registration denied."

    expiry = get_member_id_expiry(user)
    if is_id_expired(expiry):
        if context == "login":
            return "University ID has expired. Login is not allowed."
        if context == "borrow":
            return "University ID has expired. You cannot borrow books."
        return "University ID has expired. Registration denied."

    return None


def validate_campus_student_registration(*, id_number: str, full_name: str, phone: str = "", email: str = ""):
    """
    Validate campus registry before creating a self-registered student account.
    Raises rest_framework.serializers.ValidationError with a clear message.
    """
    from rest_framework import serializers

    code = str(id_number or "").strip()
    if not code:
        raise serializers.ValidationError({"id_number": "Student ID is required."})

    campus = CampusStudent.objects.filter(id_number__iexact=code).first()
    if not campus:
        raise serializers.ValidationError({"detail": "Student ID not found."})

    campus_status = str(campus.status or "").strip().upper()
    if campus_status != "ACTIVE":
        raise serializers.ValidationError({"detail": "Student is inactive."})

    if is_id_expired(campus.id_expiry_date):
        raise serializers.ValidationError({"detail": "University ID has expired. Registration denied."})

    if not names_match(full_name, campus.full_name):
        raise serializers.ValidationError(
            {"full_name": "Full name does not match campus records for this student ID."}
        )

    if User.objects.filter(id_number__iexact=code).exists():
        raise serializers.ValidationError({"detail": "An account already exists for this student ID."})

    if email and User.objects.filter(email__iexact=email.strip()).exists():
        raise serializers.ValidationError({"email": "This email is already registered."})

    if phone and campus.phone and str(campus.phone).strip() and str(phone).strip() != str(campus.phone).strip():
        raise serializers.ValidationError({"phone": "Phone number does not match campus records."})

    return campus
