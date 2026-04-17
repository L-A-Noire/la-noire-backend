"""
Comprehensive mock data seeding for LA Noire Police System
Covers all scenarios and user roles
"""
import io
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from PIL import Image as PilImage

from crime.models import Case, CaseReport, Complaint, Crime, CrimeScene
from payment.models import Transaction
from reward.models import Report, Reward
from suspect.models import Interrogation, Punishment, SuspectCrime
from suspect.models.suspect import Suspect
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

# Persian-friendly role names
ROLES_DATA = {
    "Administrator": "System Administrator",
    "Chief": "Chief of Police",
    "Captain": "Captain",
    "Sergeant": "Sergeant",
    "Detective": "Detective",
    "Officer": "Police Officer",
    "Patrol Officer": "Patrol Officer",
    "Cadet": "Police Cadet",
    "Judge": "Judge",
    "Coroner": "Medical Examiner",
    "Witness": "Witness",
    "Complainant": "Complainant",
    "Base": "Base User",
}

CRIMES = [
    {"title": "Petty Theft", "description": "Stealing small items", "level": 1},
    {"title": "Shoplifting", "description": "Shoplifting from stores", "level": 1},
    {"title": "Auto Theft", "description": "Vehicle theft", "level": 2},
    {"title": "Robbery", "description": "Armed robbery", "level": 2},
    {"title": "Assault", "description": "Physical assault", "level": 2},
    {"title": "Murder", "description": "Homicide", "level": 3},
    {"title": "Serial Murder", "description": "Multiple homicides", "level": 4},
    {"title": "Political Assassination", "description": "Targeted killing", "level": 4},
]

SUSPECT_NAMES = [
    {"first": "Jack", "last": "Nelson", "nickname": "Speedy Jack"},
    {"first": "Leland", "last": "Monroe", "nickname": "The Shadow"},
    {"first": "Michelle", "last": "Zuckerman", "nickname": "M.Z."},
    {"first": "James", "last": "Donnelly", "nickname": "The Wolf"},
    {"first": "Luis", "last": "Mendoza", "nickname": "Lucky Luis"},
    {"first": "Victor", "last": "Morose", "nickname": "V.M."},
    {"first": "Thomas", "last": "Kingston", "nickname": "The Silent"},
    {"first": "Andrew", "last": "Finney", "nickname": "Finny"},
    {"first": "Kelso", "last": "Morrison", "nickname": "K.M."},
    {"first": "Henry", "last": "Toots", "nickname": "Toast"},
]


class Command(BaseCommand):
    help = "Seed comprehensive mock data for LA Noire Police System"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Base count for generated records",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        faker = Faker()
        count = max(1, options["count"])

        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self._clear_data()

        with transaction.atomic():
            self.stdout.write("Creating roles...")
            roles = self._create_roles()

            self.stdout.write("Creating users...")
            users = self._create_users(faker, roles, count)

            self.stdout.write("Creating suspects...")
            suspects = self._create_suspects(faker, count)

            self.stdout.write("Creating crimes...")
            crimes = self._create_crimes(faker, count)

            self.stdout.write("Creating cases...")
            cases = self._create_cases(faker, crimes, users, count)

            self.stdout.write("Creating complaints...")
            self._create_complaints(faker, users, cases, count)

            self.stdout.write("Creating crime scenes...")
            self._create_crime_scenes(faker, users, cases, count)

            self.stdout.write("Creating evidence...")
            self._create_all_evidence(faker, users, cases, count)

            self.stdout.write("Creating suspect-crime relationships...")
            suspect_crimes = self._create_suspect_crimes(
                faker, suspects, crimes, users, count
            )

            self.stdout.write("Creating interrogations...")
            self._create_interrogations(faker, suspect_crimes, users, count)

            self.stdout.write("Creating punishments...")
            self._create_punishments(faker, suspect_crimes, users, count)

            self.stdout.write("Creating rewards...")
            self._create_rewards(faker, users, count)

            self.stdout.write("Creating transactions...")
            self._create_transactions(faker, count)

            self.stdout.write("Creating reports...")
            self._create_reports(faker, users, cases, suspects, count)

        self.stdout.write(
            self.style.SUCCESS("✓ Mock data successfully created!")
        )
        self.stdout.write(f"- Users: {User.objects.count()}")
        self.stdout.write(f"- Suspects: {Suspect.objects.count()}")
        self.stdout.write(f"- Crimes: {Crime.objects.count()}")
        self.stdout.write(f"- Cases: {Case.objects.count()}")
        self.stdout.write(f"- Evidence: {Evidence.objects.count()}")
        self.stdout.write(f"- Transactions: {Transaction.objects.count()}")

    def _clear_data(self):
        """Clear all data from database"""
        Transaction.objects.all().delete()
        Reward.objects.all().delete()
        Report.objects.all().delete()
        Punishment.objects.all().delete()
        Interrogation.objects.all().delete()
        SuspectCrime.objects.all().delete()
        BiologicalEvidence.objects.all().delete()
        VehicleEvidence.objects.all().delete()
        IdentificationEvidence.objects.all().delete()
        OtherEvidence.objects.all().delete()
        Testimony.objects.all().delete()
        Evidence.objects.all().delete()
        CrimeScene.objects.all().delete()
        Complaint.objects.all().delete()
        Case.objects.all().delete()
        Crime.objects.all().delete()
        CaseReport.objects.all().delete()
        Suspect.objects.all().delete()
        Image.objects.all().delete()
        Attachment.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def _create_roles(self):
        """Create all required roles"""
        roles = {}
        for role_key, role_name in ROLES_DATA.items():
            role, created = Role.objects.get_or_create(
                title=role_key, defaults={"title": role_key}
            )
            roles[role_key] = role
            if created:
                self.stdout.write(f"  ✓ Created role: {role_key}")
        return roles

    def _create_users(self, faker, roles, count):
        """Create users with different roles"""
        users = {"by_role": {}}
        role_distribution = {
            "Administrator": 1,
            "Chief": 1,
            "Captain": 2,
            "Sergeant": 3,
            "Detective": 4,
            "Officer": 5,
            "Patrol Officer": 4,
            "Cadet": 3,
            "Judge": 2,
            "Coroner": 2,
            "Witness": count * 2,
            "Complainant": count * 2,
            "Base": count,
        }

        for role_name, num_users in role_distribution.items():
            users["by_role"][role_name] = []
            for i in range(num_users):
                try:
                    user = User.objects.create_user(
                        username=faker.unique.user_name(),
                        email=faker.unique.email(),
                        phone=faker.unique.phone_number()[:20],
                        national_id=str(random.randint(10000000, 99999999)),
                        first_name=faker.first_name(),
                        last_name=faker.last_name(),
                        password="password123",
                        role=roles[role_name],
                    )
                    users["by_role"][role_name].append(user)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Could not create user: {e}")
                    )

        users["all"] = []
        for user_list in users["by_role"].values():
            users["all"].extend(user_list)

        self.stdout.write(f"  ✓ Created {len(users['all'])} users")
        return users

    def _create_suspects(self, faker, count):
        """Create suspects with various statuses"""
        suspects = []

        # Create suspects from predefined names
        for i, suspect_data in enumerate(SUSPECT_NAMES):
            try:
                status = random.choice(
                    ["suspected", "wanted", "most_wanted", "arrested"]
                )
                suspect = Suspect.objects.create(
                    name=f"{suspect_data['first']} {suspect_data['last']}",
                    nickname=suspect_data["nickname"],
                    description=faker.paragraph(nb_sentences=3),
                    gender=random.choice(["m", "f"]),
                    national_id=random.randint(10000000, 99999999),
                    status=status,
                    wanted_since=(
                        timezone.now() - timedelta(days=random.randint(1, 365))
                        if status in ["wanted", "most_wanted"]
                        else None
                    ),
                    priority_score=random.randint(0, 100),
                    reward_amount=random.randint(100000, 10000000),
                )
                suspects.append(suspect)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Could not create suspect: {e}")
                )

        # Create additional random suspects
        for _ in range(count * 2):
            try:
                status = random.choice(
                    ["suspected", "wanted", "most_wanted", "arrested", "convicted"]
                )
                suspect = Suspect.objects.create(
                    name=faker.name(),
                    nickname=faker.word().title(),
                    description=faker.paragraph(nb_sentences=2),
                    gender=random.choice(["m", "f"]),
                    national_id=random.randint(10000000, 99999999),
                    status=status,
                    wanted_since=(
                        timezone.now() - timedelta(days=random.randint(1, 180))
                        if status in ["wanted", "most_wanted"]
                        else None
                    ),
                    priority_score=random.randint(0, 100),
                    reward_amount=random.randint(0, 10000000),
                )
                suspects.append(suspect)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Could not create suspect: {e}")
                )

        self.stdout.write(f"  ✓ Created {len(suspects)} suspects")
        return suspects

    def _create_crimes(self, faker, count):
        """Create crimes with all levels"""
        crimes = []

        # Create one of each crime type
        for crime_data in CRIMES:
            crime = Crime.objects.create(level=crime_data["level"])
            crimes.append(crime)

        # Create additional random crimes
        for _ in range(count * 3):
            crime = Crime.objects.create(level=random.randint(1, 4))
            crimes.append(crime)

        self.stdout.write(f"  ✓ Created {len(crimes)} crimes")
        return crimes

    def _create_cases(self, faker, crimes, users, count):
        """Create cases from complaints and crime scenes"""
        cases = []
        detectives = users["by_role"].get("Detective", [])

        for crime in crimes[:count]:
            detective = random.choice(detectives) if detectives else None
            case = Case.objects.create(
                crime=crime,
                is_from_crime_scene=random.choice([True, False]),
                is_closed=random.choice([True, False]),
                detective=detective,
            )
            cases.append(case)

        self.stdout.write(f"  ✓ Created {len(cases)} cases")
        return cases

    def _create_complaints(self, faker, users, cases, count):
        """Create complaints"""
        cadets = users["by_role"].get("Cadet", [])
        officers = users["by_role"].get("Officer", [])
        all_users = users["all"]

        complaints = []
        for _ in range(min(count * 2, len(cases))):
            if not cadets or not officers:
                break

            complainants = random.sample(
                all_users, k=random.randint(1, min(3, len(all_users)))
            )
            complaint = Complaint.objects.create(
                description=faker.paragraph(nb_sentences=3),
                cadet=random.choice(cadets),
                police_officer=random.choice(officers),
                case=random.choice(cases) if cases else None,
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
                cadet_rejection_reason=(
                    faker.sentence() if random.choice([True, False]) else ""
                ),
            )
            complaint.complainants.add(*complainants)
            complaints.append(complaint)

        self.stdout.write(f"  ✓ Created {len(complaints)} complaints")

    def _create_crime_scenes(self, faker, users, cases, count):
        """Create crime scenes"""
        officers = users["by_role"].get("Officer", [])
        patrol_officers = users["by_role"].get("Patrol Officer", [])
        all_users = users["all"]

        scenes = []
        for case in cases[: min(count, len(cases))]:
            scene = CrimeScene.objects.create(
                crime=case.crime if case.crime else None,
                examiner=random.choice(all_users) if all_users else None,
                is_confirmed=random.choice([True, False]),
                seen_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                location=faker.address(),
                description=faker.paragraph(nb_sentences=3),
                witness=random.choice(all_users) if all_users else None,
            )
            scenes.append(scene)

        self.stdout.write(f"  ✓ Created {len(scenes)} crime scenes")

    def _create_all_evidence(self, faker, users, cases, count):
        """Create all types of evidence"""
        all_users = users["all"]
        coroners = users["by_role"].get("Coroner", [])
        images = self._create_images(users, count)
        attachments = self._create_attachments(faker, users, count)

        evidence_count = 0

        # Biological Evidence
        for _ in range(count):
            if cases:
                evidence = BiologicalEvidence.objects.create(
                    case=random.choice(cases),
                    title=random.choice(["Blood Sample", "Hair Sample", "DNA Evidence"]),
                    description=faker.paragraph(nb_sentences=2),
                    seen_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(all_users) if all_users else None,
                    location=faker.address(),
                    coronary=random.choice(coroners) if coroners else None,
                    result=faker.paragraph(nb_sentences=2) if random.choice([True, False]) else None,
                )
                if images:
                    evidence.images.add(
                        *random.sample(images, k=min(2, len(images)))
                    )
                evidence_count += 1

        # Vehicle Evidence
        for _ in range(count):
            if cases:
                use_serial = random.choice([True, False])
                evidence = VehicleEvidence.objects.create(
                    case=random.choice(cases),
                    title="Vehicle Evidence",
                    description=faker.paragraph(nb_sentences=2),
                    seen_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(all_users) if all_users else None,
                    location=faker.address(),
                    vehicle_model=faker.word().title(),
                    registration_plate_number=(
                        f"{random.randint(10, 99)}-{faker.bothify(text='???')}-{random.randint(100, 999)}"
                        if not use_serial
                        else None
                    ),
                    color=faker.color_name(),
                    serial_number=(
                        faker.bothify(text="VIN-########") if use_serial else None
                    ),
                )
                evidence_count += 1

        # Identification Evidence
        for _ in range(count):
            if cases:
                evidence = IdentificationEvidence.objects.create(
                    case=random.choice(cases),
                    title="ID Document",
                    description=faker.paragraph(nb_sentences=2),
                    seen_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(all_users) if all_users else None,
                    location=faker.address(),
                    owner_first_name=faker.first_name(),
                    owner_last_name=faker.last_name(),
                    information={
                        "id_type": random.choice(["Passport", "Driver License", "ID Card"]),
                        "number": faker.bothify(text="##########"),
                    },
                )
                evidence_count += 1

        # Testimony
        for _ in range(count):
            if cases:
                testimony = Testimony.objects.create(
                    case=random.choice(cases),
                    title="Witness Statement",
                    description=faker.paragraph(nb_sentences=2),
                    seen_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(all_users) if all_users else None,
                    location=faker.address(),
                    transcription=faker.paragraph(nb_sentences=5),
                    is_confirmed=random.choice([True, False]),
                )
                if attachments:
                    testimony.attachments.add(
                        *random.sample(
                            attachments, k=min(2, len(attachments))
                        )
                    )
                evidence_count += 1

        # Other Evidence
        for _ in range(count):
            if cases:
                evidence = OtherEvidence.objects.create(
                    case=random.choice(cases),
                    title="Physical Evidence",
                    description=faker.paragraph(nb_sentences=2),
                    seen_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(all_users) if all_users else None,
                    location=faker.address(),
                )
                evidence_count += 1

        self.stdout.write(f"  ✓ Created {evidence_count} evidence items")

    def _create_images(self, users, count):
        """Create sample images"""
        all_users = users["all"]
        images = []

        for _ in range(count):
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
            try:
                img = Image.objects.create(
                    image=ContentFile(
                        buffer.getvalue(), name=f"evidence-{_}.png"
                    ),
                    uploaded_by=random.choice(all_users) if all_users else None,
                )
                images.append(img)
            except Exception:
                pass

        return images

    def _create_attachments(self, faker, users, count):
        """Create sample attachments"""
        all_users = users["all"]
        attachments = []

        for _ in range(count):
            try:
                content = ContentFile(
                    faker.text(max_nb_chars=500).encode("utf-8"),
                    name=f"attachment-{_}.txt",
                )
                attachment = Attachment.objects.create(
                    file=content,
                    provided_by=random.choice(all_users) if all_users else None,
                )
                attachments.append(attachment)
            except Exception:
                pass

        return attachments

    def _create_suspect_crimes(self, faker, suspects, crimes, users, count):
        """Create suspect-crime relationships"""
        all_users = users["all"]
        suspect_crimes = []

        for suspect in suspects[: min(count * 2, len(suspects))]:
            # Associate each suspect with 1-3 crimes
            # Use only crimes that have associated cases
            crimes_with_cases = [crime for crime in crimes if hasattr(crime, 'case') and crime.case]
            if not crimes_with_cases:
                crimes_with_cases = crimes[:min(3, len(crimes))]

            num_crimes = random.randint(1, min(3, len(crimes_with_cases)))
            for crime in random.sample(crimes_with_cases, k=num_crimes):
                suspect_crime = SuspectCrime.objects.create(
                    suspect=suspect,
                    crime=crime,
                    added_by=random.choice(all_users) if all_users else None,
                    added_at=timezone.now() - timedelta(days=random.randint(1, 180)),
                )
                suspect_crimes.append(suspect_crime)

        self.stdout.write(f"  ✓ Created {len(suspect_crimes)} suspect-crime relationships")
        return suspect_crimes

    def _create_interrogations(self, faker, suspect_crimes, users, count):
        """Create interrogations"""
        detectives = users["by_role"].get("Detective", [])
        sergeants = users["by_role"].get("Sergeant", [])

        interrogations = []
        for suspect_crime in suspect_crimes[: min(count * 2, len(suspect_crimes))]:
            interrogation = Interrogation.objects.create(
                suspect_crime=suspect_crime,
                case=suspect_crime.crime.case if suspect_crime.crime.case else None,
                location=faker.address(),
                notes=faker.paragraph(nb_sentences=4),
                detective_score=(
                    random.randint(0, 10) if detectives else None
                ),
                sergeant_score=(
                    random.randint(0, 10) if sergeants else None
                ),
                final_score=random.randint(0, 10),
            )

            if detectives:
                interrogation.interrogators.add(random.choice(detectives))
            if sergeants:
                interrogation.interrogators.add(random.choice(sergeants))

            interrogations.append(interrogation)

        self.stdout.write(f"  ✓ Created {len(interrogations)} interrogations")

    def _create_punishments(self, faker, suspect_crimes, users, count):
        """Create punishments"""
        judges = users["by_role"].get("Judge", [])

        punishments = []
        for suspect_crime in suspect_crimes[: min(count, len(suspect_crimes))]:
            if not judges:
                break

            punishment_type = random.choice(["fine", "bail", "imprisonment"])
            punishment = Punishment.objects.create(
                suspect_crime=suspect_crime,
                punishment_type=punishment_type,
                title=f"{punishment_type.title()} for {suspect_crime.suspect.name}",
                description=faker.paragraph(nb_sentences=2),
                amount=(
                    random.randint(100000, 10000000)
                    if punishment_type in ["fine", "bail"]
                    else None
                ),
                duration_months=(
                    random.randint(1, 36) if punishment_type == "imprisonment" else None
                ),
                issued_by=random.choice(judges),
                is_paid=random.choice([True, False]) if punishment_type in ["fine", "bail"] else False,
                paid_at=(
                    timezone.now() - timedelta(days=random.randint(1, 60))
                    if punishment_type in ["fine", "bail"] and random.choice([True, False])
                    else None
                ),
            )
            punishments.append(punishment)

        self.stdout.write(f"  ✓ Created {len(punishments)} punishments")

    def _create_rewards(self, faker, users, count):
        """Create rewards"""
        all_users = users["all"]

        rewards = []
        for _ in range(count * 2):
            if not all_users:
                break

            is_claimed = random.choice([True, False])
            reward = Reward.objects.create(
                recipient=random.choice(all_users),
                amount=random.randint(1000000, 50000000),
                created_by=random.choice(all_users),
                is_claimed=is_claimed,
                claimed_at=(
                    timezone.now() - timedelta(days=random.randint(1, 30))
                    if is_claimed
                    else None
                ),
            )
            rewards.append(reward)

        self.stdout.write(f"  ✓ Created {len(rewards)} rewards")

    def _create_transactions(self, faker, count):
        """Create payment transactions"""
        transactions = []

        transaction_statuses = [
            (True, True),   # successful & used
            (True, False),  # successful & unused
            (False, False), # failed
        ]

        for _ in range(count * 3):
            is_success, is_used = random.choice(transaction_statuses)
            transaction = Transaction.objects.create(
                trans_id=faker.bothify(text="############") if is_success else None,
                id_get=faker.bothify(text="############") if is_success else None,
                amount=random.randint(10000, 50000000),
                mobile_num=faker.phone_number()[:15],
                description=faker.sentence(),
                card_number=faker.credit_card_number(),
                is_success=is_success,
                is_used=is_used if is_success else False,
            )
            transactions.append(transaction)

        self.stdout.write(f"  ✓ Created {len(transactions)} transactions")

    def _create_reports(self, faker, users, cases, suspects, count):
        """Create tips and reports"""
        all_users = users["all"]
        detectives = users["by_role"].get("Detective", [])
        officers = users["by_role"].get("Officer", [])

        reports = []

        # Reports about cases
        for case in cases[: min(count, len(cases))]:
            if all_users:
                report = Report.objects.create(
                    reporter=random.choice(all_users),
                    case=case,
                    description=faker.paragraph(nb_sentences=3),
                    status=random.choice(
                        [
                            "pending_officer",
                            "rejected_by_officer",
                            "pending_detective",
                            "rejected_by_detective",
                            "approved",
                        ]
                    ),
                    officer=(
                        random.choice(officers)
                        if officers and random.choice([True, False])
                        else None
                    ),
                    detective=(
                        random.choice(detectives)
                        if detectives and random.choice([True, False])
                        else None
                    ),
                )
                reports.append(report)

        # Reports about suspects
        for suspect in suspects[: min(count, len(suspects))]:
            if all_users:
                report = Report.objects.create(
                    reporter=random.choice(all_users),
                    suspect=suspect,
                    description=faker.paragraph(nb_sentences=3),
                    status=random.choice(
                        [
                            "pending_officer",
                            "rejected_by_officer",
                            "pending_detective",
                            "rejected_by_detective",
                            "approved",
                        ]
                    ),
                    officer=(
                        random.choice(officers)
                        if officers and random.choice([True, False])
                        else None
                    ),
                    detective=(
                        random.choice(detectives)
                        if detectives and random.choice([True, False])
                        else None
                    ),
                )
                reports.append(report)

        self.stdout.write(f"  ✓ Created {len(reports)} reports")
