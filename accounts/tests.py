from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class AccountAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            name="Test",
            last_name="User",
        )

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(reverse("register"), {
            "name": "New",
            "last_name": "Person",
            "email": "new@example.com",
            "password": "StrongPass123!",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(reverse("register"), {
            "name": "Duplicate",
            "last_name": "Person",
            "email": "user@example.com",
            "password": "StrongPass123!",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens(self):
        response = self.client.post(reverse("login"), {
            "email": "user@example.com",
            "password": "StrongPass123!",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(reverse("login"), {
            "email": "user@example.com",
            "password": "WrongPassword",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_authenticated_user(self):
        login = self.client.post(reverse("login"), {
            "email": "user@example.com",
            "password": "StrongPass123!",
        }, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(reverse("login"), {
            "email": "user@example.com",
            "password": "StrongPass123!",
        }, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post(reverse("logout"), {
            "refresh": login.data["refresh"],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
