from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from reward.models import Report, Reward
from crime.models import Case, Crime
from suspect.models import SuspectCrime
from suspect.models.suspect import Suspect
from user.models import Role

User = get_user_model()


class RewardModuleTests(APITestCase):
    def setUp(self):
        self.base_user = User.objects.create_user(
            username="base",
            password="pass123",
            email="base@gmail.com",
            role=Role.objects.get(title="Base User")
        )

        self.officer = User.objects.create_user(
            username="officer",
            password="pass123",
            email="officer@gmail.com",
            role=Role.objects.get(title="Police/Patrol Officer")
        )

        self.detective = User.objects.create_user(
            username="detective",
            password="pass123",
            email="detective@gmail.com",
            role=Role.objects.get(title="Detective")
        )

        self.crime = Crime.objects.create(
            level=4
        )

        self.case = Case.objects.create(
            crime=self.crime
        )

        self.suspect = Suspect.objects.create(
            name="Suspect A",
            wanted_since=timezone.now(),
            status="most_wanted",
        )

        self.suspect_crime = SuspectCrime.objects.create(
            crime=self.crime,
            suspect=self.suspect,
            added_by=self.officer,
        )

    def test_report_creation_requires_case_or_suspect(self):
        self.client.force_authenticate(self.base_user)

        url = reverse("report-list")
        response = self.client.post(url, {"description": "Tip"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_base_user_can_create_report(self):
        self.client.force_authenticate(self.base_user)

        url = reverse("report-list")
        response = self.client.post(
            url,
            {"case": self.case.id, "description": "Important tip"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Report.objects.first().status, "pending_officer")

    def test_officer_approves_report(self):
        report = Report.objects.create(
            reporter=self.base_user,
            case=self.case,
            description="Test",
        )

        self.client.force_authenticate(self.officer)

        url = reverse("report-review-officer", args=[report.id])
        response = self.client.put(url, {"is_approved": True}, format="json")

        report.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(report.status, "pending_detective")
        self.assertEqual(report.officer, self.officer)

    def test_detective_approval_creates_reward(self):
        report = Report.objects.create(
            reporter=self.base_user,
            suspect=self.suspect,
            description="Found suspect",
            status="pending_detective",
        )

        self.client.force_authenticate(self.detective)

        url = reverse("report-review-detective", args=[report.id])
        response = self.client.put(url, {"is_approved": True}, format="json")

        report.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(report.status, "approved")
        self.assertIsNotNone(report.reward)
        self.assertEqual(Reward.objects.count(), 1)

    def test_claim_reward_success(self):
        reward = Reward.objects.create(
            recipient=self.base_user,
            amount=10000,
            created_by=self.detective,
        )

        self.client.force_authenticate(self.base_user)

        url = "/api/reward/rewards/claim/"
        response = self.client.post(
            url,
            {"reward_code": str(reward.unique_code)},
            format="json",
        )

        reward.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(reward.is_claimed)
        self.assertIsNotNone(reward.claimed_at)

    def test_cannot_claim_used_reward(self):
        reward = Reward.objects.create(
            is_claimed=True,
            claimed_at=timezone.now(),
        )

        self.client.force_authenticate(self.base_user)

        url = "/api/reward/rewards/claim/"
        response = self.client.post(
            url,
            {"reward_code": str(reward.unique_code)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_base_user_sees_only_own_reports(self):
        Report.objects.create(
            reporter=self.base_user,
            case=self.case,
            description="Mine",
        )

        other_user = User.objects.create_user(
            username="other",
            password="pass123",
            email="other@gmail.com",
            role=Role.objects.get(title="Base User"),
        )

        Report.objects.create(
            reporter=other_user,
            case=self.case,
            description="Not mine",
        )

        self.client.force_authenticate(self.base_user)

        url = reverse("report-list")
        response = self.client.get(url)

        self.assertEqual(len(response.data), 1)
