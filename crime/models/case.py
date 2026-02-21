from django.db import models


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
