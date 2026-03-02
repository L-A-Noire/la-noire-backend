"""
Create a Case with related data for testing the timeline API.
Run: python manage.py seed_case_timeline
"""

import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from crime.models import Case, CaseReport, Complaint, Crime, CrimeScene
from user.models import Role, User


class Command(BaseCommand):
    help = "Create a Case with complaints, crime_scenes, and reports for timeline API testing"

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get or create roles
            detective_role, _ = Role.objects.get_or_create(
                title="Detective", defaults={"title": "Detective"}
            )
            cadet_role, _ = Role.objects.get_or_create(
                title="Cadet", defaults={"title": "Cadet"}
            )
            officer_role, _ = Role.objects.get_or_create(
                title="Police/Patrol Officer",
                defaults={"title": "Police/Patrol Officer"},
            )

            # Get existing users by role or create new ones
            suffix = uuid.uuid4().hex[:8]
            detective = User.objects.filter(role=detective_role).first()
            if not detective:
                detective = User.objects.create_user(
                    username=f"detective_{suffix}",
                    email=f"detective_{suffix}@test.com",
                    first_name="Test",
                    last_name="Detective",
                    password="TestPass123!",
                    role=detective_role,
                )

            cadet = User.objects.filter(role=cadet_role).first()
            if not cadet:
                cadet = User.objects.create_user(
                    username=f"cadet_{suffix}",
                    email=f"cadet_{suffix}@test.com",
                    first_name="Test",
                    last_name="Cadet",
                    password="TestPass123!",
                    role=cadet_role,
                )

            officer = User.objects.filter(role=officer_role).first()
            if not officer:
                officer = User.objects.create_user(
                    username=f"officer_{suffix}",
                    email=f"officer_{suffix}@test.com",
                    first_name="Test",
                    last_name="Officer",
                    password="TestPass123!",
                    role=officer_role,
                )

            complainant = (
                User.objects.filter(role=cadet_role).exclude(id=cadet.id).first()
            )
            if not complainant:
                complainant = cadet

            # 1. Crime
            crime = Crime.objects.create(level=2)

            # 2. Case
            case = Case.objects.create(
                crime=crime,
                is_from_crime_scene=False,
                is_closed=False,
                detective=detective,
            )

            # 3. Complaint (Complaint.case → Case)
            complaint = Complaint.objects.create(
                description="Test complaint for timeline - someone stole my bike",
                cadet=cadet,
                police_officer=officer,
                case=case,
                status="approved",
            )
            complaint.complainants.add(complainant)

            # 4. CaseReport (CaseReport.case → Case)
            CaseReport.objects.create(
                reporter=officer,
                case=case,
                description="Initial report: crime scene examined, evidence collected.",
                status="approved",
            )

            # 5. CrimeScene (CrimeScene.crime → Crime, Case.crime → Crime)
            CrimeScene.objects.create(
                crime=crime,
                examiner=officer,
                witness=complainant,
                seen_at=timezone.now() - timedelta(hours=2),
                location="123 Main Street, Downtown",
                description="Bicycle theft occurred near the park entrance.",
                is_confirmed=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCase created successfully!\n"
                f"  Case ID: {case.id}\n"
                f"  Assigned Detective: {detective.get_full_name() or detective.username}\n"
                f"  Opened Date: {case.created_at}\n"
                f"  Test timeline API: GET /api/crime/cases/{case.id}/timeline/\n"
                f"  Complaints: 1 | Crime scenes: 1 | Reports: 1\n"
            )
        )
