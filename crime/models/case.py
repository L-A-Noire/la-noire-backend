from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.db.models.signals import pre_save
from django.dispatch import receiver

from user.models import User


class Case(models.Model):
    crime = models.OneToOneField(
        to="Crime",
        on_delete=models.PROTECT,
        related_name="case",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_from_crime_scene = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    detective = models.ForeignKey(
        to="user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detective_cases",
        limit_choices_to={"role__title": "Detective"},
    )


@receiver(pre_save, sender=Case)
def assign_detective(sender, instance, **kwargs):
    if instance.detective:
        return
    detectives = (
        User.objects.filter(role__title="Detective")
        .annotate(case_count=Count("detective_cases"))
        .order_by("case_count")
    )
    if not detectives:
        raise ValidationError("No detectives available at the moment.")
    instance.detective = detectives.first()
