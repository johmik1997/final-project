from dataclasses import dataclass, field
from typing import List

from django.utils import timezone
from django.db import transaction

from .models import Borrow, Reservation
from user_mgt.access import get_active_library_policy
from material_mgt.services import send_templated_email_background

@dataclass
class OverdueNotificationSummary:
    scanned: int = 0
    status_updated: int = 0
    emailed: int = 0
    skipped_missing_email: int = 0
    errors: List[str] = field(default_factory=list)

@dataclass
class ReservationNotificationSummary:
    material_id: str
    scanned: int = 0
    emailed: int = 0
    skipped_missing_email: int = 0
    errors: List[str] = field(default_factory=list)

def process_overdue_borrows_and_notify():
    """
    Main entry point for cron jobs to sync statuses and email users.
    """
    now = timezone.now()
    summary = OverdueNotificationSummary()

    # 1. First, sync the database status for all overdue items
    summary.status_updated = sync_overdue_borrow_statuses(now=now)

    # 2. Fetch those that need notification
    overdue_qs = Borrow.objects.select_related("member", "material").filter(
        status__in=["BORROWED", "OVERDUE"],
        due_date__lt=now,
        overdue_notified_at__isnull=True
    )
    
    summary.scanned = overdue_qs.count()

    for borrow in overdue_qs:
        overdue_days = (now.date() - borrow.due_date.date()).days
        
        try:
            from user_mgt.models import Notification
            Notification.objects.create(
                member_id=borrow.member,
                borrow_id=borrow,
                message=f"Warning: Your borrow of '{borrow.material.title}' is overdue by {overdue_days} days! Please return it.",
                status='UNREAD'
            )
        except Exception as e:
            print(f"Error creating system notification for overdue: {e}")

        member_email = (borrow.member.email or "").strip()
        if not member_email:
            summary.skipped_missing_email += 1
            borrow.overdue_notified_at = now
            borrow.save(update_fields=["overdue_notified_at"])
            continue

        member_name = (borrow.member.first_name or borrow.member.id_number).strip()
        
        try:
            send_templated_email_background(
                template_name="overdue_borrow",
                context={
                    "member_name": member_name,
                    "material_title": borrow.material.title,
                    "due_date": borrow.due_date.date().isoformat(),
                    "overdue_days": overdue_days,
                },
                recipients=[member_email],
            )
            borrow.overdue_notified_at = now
            borrow.save(update_fields=["overdue_notified_at"])
            summary.emailed += 1
        except Exception as exc:
            summary.errors.append(f"Borrow {borrow.id}: {exc}")

    return summary

def sync_overdue_borrow_statuses(base_queryset=None, now=None):
    """
    Updates the database 'status' column to OVERDUE for items past their due date.
    """
    now = now or timezone.now()
    queryset = base_queryset if base_queryset is not None else Borrow.objects.all()
    
    overdue_qs = queryset.filter(
        status__in=["BORROWED", "OVERDUE"],
        due_date__lt=now,
    ).exclude(status="OVERDUE")
    
    return overdue_qs.update(status="OVERDUE")

def notify_reserved_members_material_available(material):
    """
    Notify active reservation holders that a material copy became available.
    """
    now = timezone.now()
    summary = ReservationNotificationSummary(material_id=str(material.pk))

    active_reservations = Reservation.objects.select_related("member", "material_id").filter(
        material_id=material,
        status="RESERVED",
        expiry_date__gt=now,
        availability_notified_at__isnull=True,
    ).order_by("reserve_date")

    summary.scanned = active_reservations.count()

    for reservation in active_reservations:
        member_email = (reservation.member.email or "").strip()
        if not member_email:
            summary.skipped_missing_email += 1
            continue

        member_name = (reservation.member.first_name or reservation.member.id_number).strip()
        try:
            send_templated_email_background(
                template_name="reservation_available",
                context={
                    "member_name": member_name,
                    "material_title": reservation.material_id.title,
                },
                recipients=[member_email],
            )
            reservation.availability_notified_at = now
            reservation.save(update_fields=["availability_notified_at"])
            summary.emailed += 1
        except Exception as exc:
            summary.errors.append(f"Reservation {reservation.id}: {exc}")

    return summary


def calculate_overdue_days(due_date, now=None, grace_period_days=0):
    """
    Return overdue days as full/partial day units once due_date has passed.
    Any delay beyond due_date counts as at least 1 overdue day.
    """
    now = now or timezone.now()
    if grace_period_days:
        due_date = due_date + timezone.timedelta(days=int(grace_period_days))
    if now <= due_date:
        return 0

    overdue_seconds = (now - due_date).total_seconds()
    return int((overdue_seconds + 86399) // 86400)


def get_borrow_policy(borrow):
    library = getattr(getattr(borrow, "material", None), "library", None) or getattr(getattr(borrow, "member", None), "library", None)
    return get_active_library_policy(library)


def finalize_return_for_borrow(borrow):
    """
    Mark borrow as returned and release one copy back to inventory atomically.
    Safe to call repeatedly; only applies changes when borrow is not RETURNED.
    """
    with transaction.atomic():
        locked_borrow = Borrow.objects.select_for_update().select_related("material").get(pk=borrow.pk)
        if locked_borrow.status == "RETURNED":
            return locked_borrow

        material = locked_borrow.material.__class__.objects.select_for_update().get(pk=locked_borrow.material.pk)
        material.available_copies = min(material.available_copies + 1, material.total_copies)
        material.save(update_fields=["available_copies"])

        locked_borrow.status = "RETURNED"
        locked_borrow.save(update_fields=["status"])

        transaction.on_commit(lambda: notify_reserved_members_material_available(material))
        return locked_borrow


def notify_borrow_success(borrow):
    try:
        from user_mgt.models import Notification
        Notification.objects.create(
            member_id=borrow.member,
            borrow_id=borrow,
            message=f"You successfully borrowed '{borrow.material.title}'. Due date: {borrow.due_date.date().isoformat()}.",
            status='UNREAD'
        )
    except Exception as e:
        print(f"Error creating system notification for borrow: {e}")

    member_email = (borrow.member.email or "").strip()
    if not member_email:
        return
    member_name = (borrow.member.first_name or borrow.member.id_number).strip()
    send_templated_email_background(
        template_name="borrow_success",
        context={
            "member_name": member_name,
            "material_title": borrow.material.title,
            "due_date": borrow.due_date.date().isoformat(),
        },
        recipients=[member_email],
    )


def notify_return_success(borrow, return_record):
    try:
        from user_mgt.models import Notification
        fine_str = f" Fine: ${return_record.fine_amount}." if return_record.fine_amount else ""
        Notification.objects.create(
            member_id=borrow.member,
            borrow_id=borrow,
            message=f"You successfully returned '{borrow.material.title}'.{fine_str}",
            status='UNREAD'
        )
    except Exception as e:
        print(f"Error creating system notification for return: {e}")

    member_email = (borrow.member.email or "").strip()
    if not member_email:
        return
    member_name = (borrow.member.first_name or borrow.member.id_number).strip()
    send_templated_email_background(
        template_name="return_success",
        context={
            "member_name": member_name,
            "material_title": borrow.material.title,
            "fine_amount": return_record.fine_amount,
        },
        recipients=[member_email],
    )


def notify_circulation_borrow_success(circulation):
    # 1. System notification in database
    try:
        from user_mgt.models import Notification
        Notification.objects.create(
            member_id=circulation.member,
            message=f"You successfully borrowed '{circulation.material.title}' from Front Desk. Location: SHELF.",
            status='UNREAD'
        )
    except Exception as e:
        print(f"Error creating system notification for circulation borrow: {e}")

    # 2. Email notification
    member_email = (circulation.member.email or "").strip()
    if not member_email:
        return
    member_name = (circulation.member.first_name or circulation.member.id_number).strip()
    try:
        send_templated_email_background(
            template_name="borrow_success",
            context={
                "member_name": member_name,
                "material_title": circulation.material.title,
                "due_date": "N/A (Shelf Circulation)",
            },
            recipients=[member_email],
        )
    except Exception as e:
        print(f"Error sending email for circulation borrow: {e}")


def notify_circulation_return_success(circulation):
    # 1. System notification in database
    try:
        from user_mgt.models import Notification
        Notification.objects.create(
            member_id=circulation.member,
            message=f"You successfully returned '{circulation.material.title}' to Front Desk.",
            status='UNREAD'
        )
    except Exception as e:
        print(f"Error creating system notification for circulation return: {e}")

    # 2. Email notification
    member_email = (circulation.member.email or "").strip()
    if not member_email:
        return
    member_name = (circulation.member.first_name or circulation.member.id_number).strip()
    try:
        send_templated_email_background(
            template_name="return_success",
            context={
                "member_name": member_name,
                "material_title": circulation.material.title,
                "fine_amount": 0,
            },
            recipients=[member_email],
        )
    except Exception as e:
        print(f"Error sending email for circulation return: {e}")
