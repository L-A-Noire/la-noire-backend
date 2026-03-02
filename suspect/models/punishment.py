from django.db import models


class Punishment(models.Model):
    PUNISHMENT_TYPES = (
        ("fine", "Fine"),
        ("bail", "Bail"),
        ("imprisonment", "Imprisonment"),
        ("death", "Death"),
    )

    suspect_crime = models.OneToOneField(
        to="SuspectCrime", on_delete=models.PROTECT, related_name="punishment"
    )

    punishment_type = models.CharField(max_length=20, choices=PUNISHMENT_TYPES)

    title = models.CharField(max_length=200)

    description = models.TextField()

    amount = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)

    is_paid = models.BooleanField(default=False)

    paid_at = models.DateTimeField(null=True, blank=True)

    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    duration_months = models.IntegerField(null=True, blank=True)

    issued_by = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="issued_punishments",
        help_text="Judge who issued the punishment",
    )

    issued_at = models.DateTimeField(auto_now_add=True)
