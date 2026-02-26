from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from crime.models import Crime
from suspect.models.suspect import Suspect


class SuspectCrime(models.Model):
    suspect = models.ForeignKey(
        to=Suspect,
        on_delete=models.PROTECT,
        related_name="suspected_crimes",
    )

    crime = models.ForeignKey(
        to=Crime,
        on_delete=models.PROTECT,
        related_name="suspects",
        null=True,
        blank=True,
    )

    added_at = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="added_suspects",
    )


@receiver(post_save, sender=SuspectCrime)
def update_suspect(sender, instance, **kwargs):
    instance.suspect.save()
