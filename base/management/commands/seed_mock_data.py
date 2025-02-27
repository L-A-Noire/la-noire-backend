import io
import random
import uuid

from detective_board.models import BoardConnection, BoardItem, DetectiveBoard
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from PIL import Image as PilImage

from crime.models import Case, CaseReport, Complaint, Crime, CrimeScene
from reward.models import Payment, Report, Reward
from suspect.models import Interrogation, Punishment, SuspectCrime
from user.models import Role, User
from witness.models import (
    Attachment,
    BiologicalEvidence,
    Evidence,
    IdentificationEvidence,
    Image,
    OtherEvidence,
    Testimony,
    VehicleEvidence,
)

ROLE_TITLES = [
    "Detective",
    "Sergeant",
    "Cadet",
    "Officer",
    "Judge",
    "Coronary",
    "Witness",
    "Suspect",
]


class Command(BaseCommand):
    help = "Seed mock data for all models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Base count for generated records",
        )

    def handle(self, *args, **options):
        faker = Faker()
        count = max(1, options["count"])

        with transaction.atomic():
            roles = self._ensure_roles()

            users = []
            for role in roles.values():
                users.append(self._create_user(faker, role))
            for _ in range(count * 4):
                role = random.choice(list(roles.values()))
                users.append(self._create_user(faker, role))

            detectives = [u for u in users if u.role.title == "Detective"]
            sergeants = [u for u in users if u.role.title == "Sergeant"]
            cadets = [u for u in users if u.role.title == "Cadet"]
            officers = [u for u in users if u.role.title == "Officer"]
            judges = [u for u in users if u.role.title == "Judge"]
            coronaries = [u for u in users if u.role.title == "Coronary"]

            crimes = [self._create_crime(faker) for _ in range(count)]
            cases = [
                self._create_case(crime, random.choice(detectives)) for crime in crimes
            ]

            case_reports = [
                self._create_case_report(faker, random.choice(users), case)
                for case in cases
            ]

            for _ in range(count):
                complainants = random.sample(users, k=min(2, len(users)))
                self._create_complaint(
                    faker,
                    complainants,
                    random.choice(cadets),
                    random.choice(officers),
                    random.choice(cases),
                )

            for _ in range(count):
                scene = self._create_crime_scene(
                    faker,
                    random.choice(users),
                    random.choice(case_reports),
                    random.choice(users),
                )
                scene.witnesses.add(*random.sample(users, k=min(3, len(users))))

            attachments = [
                self._create_attachment(faker, random.choice(users))
                for _ in range(count)
            ]
            images = [self._create_image(random.choice(users)) for _ in range(count)]

            evidences = [
                self._create_evidence(faker, random.choice(users)) for _ in range(count)
            ]

            biological = [
                self._create_biological_evidence(
                    faker,
                    random.choice(users),
                    random.choice(coronaries) if coronaries else None,
                    images,
                )
                for _ in range(count)
            ]

            identification = [
                self._create_identification_evidence(faker, random.choice(users))
                for _ in range(count)
            ]

            other = [
                self._create_other_evidence(faker, random.choice(users))
                for _ in range(count)
            ]

            testimonies = [
                self._create_testimony(faker, random.choice(users), attachments)
                for _ in range(count)
            ]

            vehicles = [
                self._create_vehicle_evidence(faker, random.choice(users))
                for _ in range(count)
            ]

            all_evidence = (
                evidences + biological + identification + other + testimonies + vehicles
            )

            for _ in range(count):
                suspect_crime = self._create_suspect_crime(
                    random.choice(users),
                    random.choice(cases),
                    random.choice(users),
                )

                interrogation = self._create_interrogation(
                    faker,
                    suspect_crime,
                    suspect_crime.case,
                )
                if detectives or sergeants:
                    interrogators = []
                    if detectives:
                        interrogators.append(random.choice(detectives))
                    if sergeants:
                        interrogators.append(random.choice(sergeants))
                    interrogation.interrogators.add(*interrogators)

                if judges:
                    self._create_punishment(
                        faker,
                        suspect_crime,
                        random.choice(cases),
                        random.choice(judges),
                    )

            rewards = [
                self._create_reward(random.choice(users), random.choice(users))
                for _ in range(count)
            ]

            for reward in rewards:
                self._create_payment(faker, reward, random.choice(users))

            for _ in range(count):
                self._create_report_case(
                    faker,
                    random.choice(users),
                    random.choice(cases),
                )

            for _ in range(count):
                self._create_report_suspect(
                    faker,
                    random.choice(users),
                    random.choice(SuspectCrime.objects.all()),
                )

            if detectives and all_evidence:
                board = DetectiveBoard.objects.create(
                    detective=random.choice(detectives)
                )
                item1 = BoardItem.objects.create(
                    board=board,
                    evidence=random.choice(all_evidence),
                    x_position=random.random() * 100,
                    y_position=random.random() * 100,
                )
                item2 = BoardItem.objects.create(
                    board=board,
                    evidence=random.choice(all_evidence),
                    x_position=random.random() * 100,
                    y_position=random.random() * 100,
                )
                if item1 != item2:
                    BoardConnection.objects.create(from_item=item1, to_item=item2)

        self.stdout.write(self.style.SUCCESS("Mock data created"))

    def _ensure_roles(self):
        roles = {}
        for title in ROLE_TITLES:
            role, _ = Role.objects.get_or_create(title=title)
            roles[title] = role
        return roles

    def _create_user(self, faker, role):
        user = User.objects.create_user(
            username=faker.unique.user_name(),
            email=faker.unique.email(),
            phone=faker.unique.msisdn(),
            national_id=faker.unique.ssn(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password="Password123!",
            role=role,
        )
        return user

    def _create_crime(self, faker):
        return Crime.objects.create(
            level=random.choice(["1", "2", "3", "4"]),
        )

    def _create_case(self, crime, detective):
        return Case.objects.create(
            crime=crime,
            is_from_crime_scene=random.choice([True, False]),
            is_closed=random.choice([True, False]),
            detective=detective,
        )

    def _create_case_report(self, faker, reporter, case):
        return CaseReport.objects.create(
            reporter=reporter,
            case=case,
            description=faker.paragraph(nb_sentences=4),
            status=random.choice(["pending", "approved", "rejected"]),
        )

    def _create_complaint(self, faker, complainants, cadet, officer, case):
        complaint = Complaint.objects.create(
            description=faker.paragraph(nb_sentences=2),
            cadet=cadet,
            police_officer=officer,
            case=case,
            status=random.choice(
                [
                    "pending_cadet",
                    "rejected_by_cadet",
                    "pending_officer",
                    "rejected_by_officer",
                    "approved",
                    "invalid",
                ]
            ),
            cadet_rejection_reason=faker.sentence(),
            officer_rejection_reason=faker.sentence(),
        )
        if complainants:
            complaint.complainants.add(*complainants)
        return complaint

    def _create_crime_scene(self, faker, viewer, case_report, examiner):
        return CrimeScene.objects.create(
            viewer=viewer,
            case_report=case_report,
            examiner=examiner,
            is_confirmed=random.choice([True, False]),
            seen_at=faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            location=faker.address(),
            description=faker.paragraph(nb_sentences=2),
        )

    def _create_attachment(self, faker, provided_by):
        content = ContentFile(
            faker.text(max_nb_chars=200).encode("utf-8"),
            name=f"attachment-{uuid.uuid4().hex}.txt",
        )
        return Attachment.objects.create(
            file=content,
            provided_by=provided_by,
        )

    def _create_image(self, uploaded_by):
        buffer = io.BytesIO()
        image = PilImage.new(
            "RGB",
            (200, 200),
            color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        )
        image.save(buffer, format="PNG")
        return Image.objects.create(
            image=ContentFile(buffer.getvalue(), name=f"image-{uuid.uuid4().hex}.png"),
            uploaded_by=uploaded_by,
        )

    def _create_evidence(self, faker, created_by):
        return Evidence.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
        )

    def _create_biological_evidence(self, faker, created_by, coronary, images):
        evidence = BiologicalEvidence.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
            coronary=coronary,
            result=faker.paragraph(nb_sentences=2),
        )
        if images:
            evidence.images.add(*random.sample(images, k=min(2, len(images))))
        return evidence

    def _create_identification_evidence(self, faker, created_by):
        return IdentificationEvidence.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
            owner_first_name=faker.first_name(),
            owner_last_name=faker.last_name(),
            information={"note": faker.sentence()},
        )

    def _create_other_evidence(self, faker, created_by):
        return OtherEvidence.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
        )

    def _create_testimony(self, faker, created_by, attachments):
        testimony = Testimony.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
            transcription=faker.paragraph(nb_sentences=4),
        )
        if attachments:
            testimony.attachments.add(
                *random.sample(attachments, k=min(2, len(attachments)))
            )
        return testimony

    def _create_vehicle_evidence(self, faker, created_by):
        use_serial = random.choice([True, False])
        serial_number = faker.bothify(text="??######") if use_serial else None
        plate_number = faker.bothify(text="##-???-###") if not use_serial else None
        return VehicleEvidence.objects.create(
            title=faker.word(),
            description=faker.paragraph(nb_sentences=2),
            created_at=timezone.now(),
            created_by=created_by,
            vehicle_model=faker.word().title(),
            registration_plate_number=plate_number,
            color=faker.color_name(),
            serial_number=serial_number,
        )

    def _create_suspect_crime(self, suspect, case, added_by):
        return SuspectCrime.objects.create(
            suspect=suspect,
            case=case,
            added_by=added_by,
            status=random.choice(
                ["suspect", "most_wanted", "arrested", "convicted", "innocent"]
            ),
            wanted_since=timezone.now(),
            priority_score=random.randint(0, 100),
            reward_amount=random.randint(0, 100000),
        )

    def _create_interrogation(self, faker, suspect_crime, case):
        return Interrogation.objects.create(
            suspect_crime=suspect_crime,
            case=case,
            location=faker.address(),
            notes=faker.paragraph(nb_sentences=3),
            detective_score=random.randint(0, 100),
            sergeant_score=random.randint(0, 100),
            final_score=random.randint(0, 100),
        )

    def _create_punishment(self, faker, suspect_crime, case, issued_by):
        punishment_type = random.choice(["fine", "bail", "imprisonment", "death"])
        return Punishment.objects.create(
            suspect_crime=suspect_crime,
            case=case,
            punishment_type=punishment_type,
            title=faker.sentence(nb_words=4),
            description=faker.paragraph(nb_sentences=2),
            amount=(
                random.randint(1000, 50000)
                if punishment_type in ["fine", "bail"]
                else None
            ),
            duration_months=(
                random.randint(1, 36) if punishment_type == "imprisonment" else None
            ),
            issued_by=issued_by,
        )

    def _create_reward(self, recipient, created_by):
        is_claimed = random.choice([True, False])
        return Reward.objects.create(
            recipient=recipient,
            amount=random.randint(1000, 50000),
            is_claimed=is_claimed,
            claimed_at=timezone.now() if is_claimed else None,
            created_by=created_by,
        )

    def _create_payment(self, faker, reward, processed_by):
        return Payment.objects.create(
            reward=reward,
            processed_by=processed_by,
            recipient_national_id=faker.ssn(),
            recipient_full_name=faker.name(),
            payment_reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
        )

    def _create_report_case(self, faker, reporter, case):
        return Report.objects.create(
            reporter=reporter,
            case=case,
            description=faker.paragraph(nb_sentences=2),
            status=random.choice(
                [
                    "pending_officer",
                    "rejected_by_officer",
                    "pending_detective",
                    "rejected_by_detective",
                    "approved",
                ]
            ),
        )

    def _create_report_suspect(self, faker, reporter, suspect):
        return Report.objects.create(
            reporter=reporter,
            suspect=suspect,
            description=faker.paragraph(nb_sentences=2),
            status=random.choice(
                [
                    "pending_officer",
                    "rejected_by_officer",
                    "pending_detective",
                    "rejected_by_detective",
                    "approved",
                ]
            ),
        )
