from django.db import models

from witness.models.attachment import Attachment
from witness.models.evidence import Evidence


class Testimony(Evidence):
    transcription = models.TextField()

    attachments = models.ManyToManyField(
        Attachment,
    )
