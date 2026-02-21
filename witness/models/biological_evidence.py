from django.db import models

from user.models import User
from witness.models.evidence import Evidence
from witness.models.image import Image


class BiologicalEvidence(Evidence):
    images = models.ManyToManyField(
        Image,
    )

    coronary = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    result = models.TextField(blank=True, null=True)
