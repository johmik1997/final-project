from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from user_mgt.models import CampusStudent


SAMPLE_STUDENTS = [
    {
        "id_number": "STU10001",
        "full_name": "Abebe Kebede",
        "phone": "0911000001",
        "department": "Computer Science",
        "campus": "Main Campus",
        "status": "ACTIVE",
        "id_expiry_date": timezone.localdate() + timedelta(days=365),
    },
    {
        "id_number": "STU10002",
        "full_name": "Sara Tesfaye",
        "phone": "0911000002",
        "department": "Software Engineering",
        "campus": "Technology Campus",
        "status": "ACTIVE",
        "id_expiry_date": timezone.localdate() + timedelta(days=180),
    },
    {
        "id_number": "STU10003",
        "full_name": "Dawit Hailu",
        "phone": "0911000003",
        "department": "Information Technology",
        "campus": "Main Campus",
        "status": "INACTIVE",
        "id_expiry_date": timezone.localdate() + timedelta(days=90),
    },
    {
        "id_number": "STU10004",
        "full_name": "Hanna Girma",
        "phone": "0911000004",
        "department": "Nursing",
        "campus": "Hawassa Referral Campus",
        "status": "ACTIVE",
        "id_expiry_date": timezone.localdate() - timedelta(days=30),
    },
]


class Command(BaseCommand):
    help = "Seed campus_students test records for student self-registration."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for row in SAMPLE_STUDENTS:
            obj, was_created = CampusStudent.objects.update_or_create(
                id_number=row["id_number"],
                defaults=row,
            )
            if was_created:
                created += 1
            else:
                updated += 1
            self.stdout.write(f"  {obj.id_number} ({obj.status})")

        self.stdout.write(self.style.SUCCESS(f"Done. created={created}, updated={updated}"))
