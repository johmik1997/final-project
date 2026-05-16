from rest_framework import status
from rest_framework.test import APITestCase

from user_mgt.models import Library, User


class MemberLibraryAssignmentTests(APITestCase):
    def setUp(self):
        self.library_a = Library.objects.create(
            name="Main Library",
            campus="Main Campus",
            location="Block A",
            phone="0911223344",
        )
        self.library_b = Library.objects.create(
            name="IoT Library",
            campus="IoT Campus",
            location="Block B",
            phone="0911223345",
        )
        self.admin = User.objects.create_user(
            id_number="ADM-100",
            email="admin@example.com",
            password="StrongPass123!",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            library=self.library_a,
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)

    def test_member_creation_clears_library_assignment(self):
        response = self.client.post(
            "/api/user/users/create/",
            {
                "id_number": "MEM-101",
                "first_name": "Member",
                "last_name": "User",
                "email": "member101@example.com",
                "role": "MEMBER",
                "status": "ACTIVE",
                "library": str(self.library_b.id),
                "password": "StrongPass123!",
                "phone": "0911223346",
                "department": "Computer Science",
                "user_type": "STUDENT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(id_number="MEM-101")
        self.assertIsNone(created_user.library_id)

    def test_admin_user_list_includes_global_members(self):
        member = User.objects.create_user(
            id_number="MEM-102",
            email="member102@example.com",
            password="StrongPass123!",
            first_name="Visible",
            last_name="Member",
            role="MEMBER",
            department="Computer Science",
            user_type="STUDENT",
        )

        response = self.client.get("/api/user/users/all")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("result", response.data if isinstance(response.data, list) else [])
        returned_ids = {row["id"] for row in results}
        self.assertIn(str(member.id), returned_ids)

    def test_admin_can_update_global_member(self):
        member = User.objects.create_user(
            id_number="MEM-103",
            email="member103@example.com",
            password="StrongPass123!",
            first_name="Before",
            last_name="Member",
            role="MEMBER",
            department="Computer Science",
            user_type="STUDENT",
        )

        response = self.client.put(
            f"/api/user/users/update/{member.id}/",
            {
                "id_number": member.id_number,
                "first_name": "After",
                "last_name": member.last_name,
                "email": member.email,
                "role": "MEMBER",
                "status": "ACTIVE",
                "phone": member.phone or "0911223347",
                "department": member.department,
                "user_type": member.user_type,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertEqual(member.first_name, "After")
        self.assertIsNone(member.library_id)
