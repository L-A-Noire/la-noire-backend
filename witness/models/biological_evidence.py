from django.db import models

from user.models import User
from witness.models.evidence import Evidence
from witness.models.image import Image


class BiologicalEvidence(Evidence):
    images = models.ManyToManyField(
        Image,
        related_name="biological_evidence",
    )

    coronary = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="coronary_evidence",
    )

    result = models.TextField(blank=True, null=True)
