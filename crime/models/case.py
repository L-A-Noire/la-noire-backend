from django.db import models


class Case(models.Model):
    crime = models.OneToOneField(
        to='Crime',
        on_delete=models.PROTECT,
        related_name='case',
        null=True,
        blank=True,
    )
