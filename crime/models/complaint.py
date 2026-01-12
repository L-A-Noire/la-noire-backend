from django.db import models


class Complaint(models.Model):
    complainants = models.ManyToManyField(
        to="user.User",
        related_name="complaints",
    )

    description = models.TextField()

    cadet = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="cadet_complaints",
    )

    is_confirmed_by_cadet = models.BooleanField()

    rejection_reason = models.TextField()

    police_officer = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="officer_complaints",
    )

    rejection_count = models.IntegerField(
        default=0,
    )

    case = models.ForeignKey(
        to="Case",
        on_delete=models.PROTECT,
        related_name="complaints",
        null=True,
        blank=True,
    )
