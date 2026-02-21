from django.db import models

from witness.models.evidence import Evidence


class IdentificationEvidence(Evidence):
    owner_first_name = models.CharField(max_length=100)

    owner_last_name = models.CharField(max_length=100)

    information = models.JSONField(default=dict)
