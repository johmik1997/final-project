from datetime import date
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from user_mgt.models import Library, User
from material_mgt.models import DigitalMaterial, MaterialBookmark, MaterialFavorite, MaterialFeedback, PhysicalMaterial


class MaterialInteractionApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            id_number="MEM-100",
            email="member1@example.com",
            password="StrongPass123!",
            first_name="First",
            last_name="User",
            role="MEMBER",
        )
        self.other_user = User.objects.create_user(
            id_number="MEM-200",
            email="member2@example.com",
            password="StrongPass123!",
            first_name="Second",
            last_name="User",
            role="MEMBER",
        )
        self.client.force_authenticate(user=self.user)
        self.library_a = Library.objects.create(
            name="Main Library",
            campus="Main Campus",
            location="Block A",
            phone="0911000000",
        )
        self.library_b = Library.objects.create(
            name="IoT Library",
            campus="IoT Campus",
            location="Block B",
            phone="0911000001",
        )

        self.physical = PhysicalMaterial.objects.create(
            title="Physical Test Book",
            author="Author One",
            category="BOOK",
            genre="Tech",
            published_date=date(2024, 1, 1),
            department="CS",
            language="English",
            total_copies=5,
            available_copies=5,
            price=100,
            condition="GOOD",
            location="STACK",
            can_borrow=True,
            library=self.library_a,
        )

        self.digital = DigitalMaterial.objects.create(
            title="Digital Test Book",
            author="Author Two",
            category="BOOK",
            genre="Science",
            published_date=date(2024, 1, 1),
            department="CS",
            language="English",
            isbn="ISBN-10001",
            format="PDF",
            file_size="1 MB",
            file=SimpleUploadedFile("test.pdf", b"%PDF-1.4 test file", content_type="application/pdf"),
            library=self.library_b,
        )

    def test_create_feedback_and_prevent_duplicate_feedback(self):
        url = "/api/material/feedback/"
        payload = {
            "material_type": "physical",
            "material_id": str(self.physical.id),
            "rating": 5,
            "comment": "Great material.",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        duplicate = self.client.post(url, payload, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MaterialFeedback.objects.count(), 1)

    def test_favorite_is_idempotent(self):
        url = "/api/material/favorites/"
        payload = {"material_type": "digital", "material_id": str(self.digital.id)}

        first = self.client.post(url, payload, format="json")
        second = self.client.post(url, payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(MaterialFavorite.objects.count(), 1)

    def test_bookmark_list_returns_only_authenticated_user_data(self):
        MaterialBookmark.objects.create(user=self.user, physical_material=self.physical)
        MaterialBookmark.objects.create(user=self.other_user, digital_material=self.digital)

        response = self.client.get("/api/material/bookmarks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("result", response.data if isinstance(response.data, list) else [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user_id"], str(self.user.id))

    def test_interaction_stats_endpoint(self):
        MaterialFeedback.objects.create(user=self.user, physical_material=self.physical, rating=4, comment="Useful")
        MaterialFavorite.objects.create(user=self.user, physical_material=self.physical)
        MaterialBookmark.objects.create(user=self.user, physical_material=self.physical)

        response = self.client.get(
            "/api/material/interactions/stats/",
            {"material_type": "physical", "material_id": str(self.physical.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ratings_count"], 1)
        self.assertEqual(response.data["favorites_count"], 1)
        self.assertEqual(response.data["bookmarks_count"], 1)
        self.assertTrue(response.data["is_favorited"])
        self.assertTrue(response.data["is_bookmarked"])

    def test_member_can_list_materials_from_all_libraries(self):
        response = self.client.get("/api/material/physical-materials/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("result", response.data if isinstance(response.data, list) else [])
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]["library"]), str(self.library_a.id))

    def test_member_can_favorite_material_from_any_library(self):
        response = self.client.post(
            "/api/material/favorites/",
            {"material_type": "digital", "material_id": str(self.digital.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaterialFavorite.objects.count(), 1)
        self.assertEqual(response.data["material"]["library_id"], str(self.library_b.id))


class MaterialAiApiTests(APITestCase):
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_DESCRIPTION_MODEL": "gpt-5-mini"}, clear=False)
    @patch("material_mgt.views.requests.post")
    def test_generate_description_request_omits_temperature(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"output": [{"content": [{"text": "Generated summary"}]}]}),
        )

        user = User.objects.create_user(
            id_number="MEM-300",
            email="member3@example.com",
            password="StrongPass123!",
            first_name="Third",
            last_name="User",
            role="MEMBER",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/material/generate-description/",
            {"title": "AI Book", "author": "Test Author"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_payload["model"], "gpt-5-mini")
        self.assertNotIn("temperature", request_payload)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_CHAT_MODEL": "gpt-5-mini"}, clear=False)
    @patch("material_mgt.views.requests.post")
    def test_chatbot_request_uses_backend_responses_api_without_temperature(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"output": [{"content": [{"text": "Hello from AI"}]}]}),
        )

        response = self.client.post(
            "/api/material/assistant-chat/",
            {
                "prompt": "How do reservations work?",
                "history": [{"role": "user", "content": "Hi"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_payload["model"], "gpt-5-mini")
        self.assertNotIn("temperature", request_payload)
        self.assertIn("How do reservations work?", request_payload["input"])
