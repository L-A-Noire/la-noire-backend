from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from witness.models.attachment import Attachment
from witness.models.evidence import Evidence


class Testimony(Evidence):
    transcription = models.TextField()

    attachments = models.ManyToManyField(
        Attachment,
    )

    is_confirmed = models.BooleanField(default=False)


@receiver(pre_save, sender=Testimony)
def handle_confirmation(sender, instance, **kwargs):
    if not instance.is_confirmed and instance.case is not None:
        instance.is_confirmed = True
