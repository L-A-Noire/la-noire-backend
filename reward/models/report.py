from django.db import models

from crime.models import Case
from suspect.models.suspect import Suspect


class Report(models.Model):
    reporter = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="tips"
    )

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=True, blank=True, related_name="tips"
    )

    suspect = models.ForeignKey(
        Suspect,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tips",
    )

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ("pending_officer", "Pending Officer"),
        ("rejected_by_officer", "Rejected by Officer"),
        ("pending_detective", "Pending Detective"),
        ("rejected_by_detective", "Rejected by Detective"),
        ("approved", "Approved"),
    )

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="pending_officer"
    )

    officer = models.ForeignKey(
        to="user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tips_officer",
    )

    detective = models.ForeignKey(
        to="user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tips_detective",
    )

    reward = models.OneToOneField(
        to="Reward",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="either_case_or_suspect",
                condition=(
                    models.Q(case__isnull=False, suspect__isnull=True)
                    | models.Q(case__isnull=True, suspect__isnull=False)
                ),
            )
        ]
