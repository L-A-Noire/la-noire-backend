from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import Role

User = get_user_model()


class UserModuleTests(APITestCase):

    def setUp(self):
        self.base_role = Role.objects.get(title="Base User")
        self.detective_role = Role.objects.create(title="Detective")
        self.admin_role = Role.objects.get(title="Administrator")

        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass123",
            email="admin@gmail.com",
            role=self.admin_role,
        )

        self.normal_user = User.objects.create_user(
            username="normal",
            password="pass123",
            role=self.base_role,
        )

    def test_registration_requires_identifier(self):
        url = reverse("register")
        response = self.client.post(
            url,
            {"password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_registration_assigns_base_role(self):
        url = reverse("register")

        response = self.client.post(
            url,
            {
                "username": "john",
                "password": "strongpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="john")
        self.assertEqual(user.role.title, "Base User")

    def test_login_fails_with_wrong_password(self):
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "identifier": "testuser",
                "password": "wrongpass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(
            username="testuser2",
            password="correctpass",
            role=self.base_role,
        )

        url = reverse("login")
        response = self.client.post(
            url,
            {
                "identifier": "testuser2",
                "password": "correctpass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_non_admin_cannot_create_role(self):
        self.client.force_authenticate(user=self.normal_user)

        url = reverse("role-list-create")
        response = self.client.post(
            url,
            {"title": "Detective"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_role(self):
        self.client.force_authenticate(user=self.admin_user)

        url = "/api/auth/roles/"
        response = self.client.post(
            url,
            {"title": "New User Role"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(title="New User Role").exists())
