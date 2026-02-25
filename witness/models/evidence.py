from django.db import models

from crime.models import Case
from user.models import User


class Evidence(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="evidence",
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=50,
    )

    description = models.TextField()

    seen_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )

    location = models.CharField(max_length=200)
