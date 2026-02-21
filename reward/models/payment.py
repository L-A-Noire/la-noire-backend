from django.db import models


class Payment(models.Model):
    reward = models.OneToOneField(
        to="Reward", on_delete=models.PROTECT, related_name="payment"
    )

    processed_by = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="processed_payments"
    )

    processed_at = models.DateTimeField(auto_now_add=True)

    recipient_national_id = models.CharField(max_length=20)
    recipient_full_name = models.CharField(max_length=200)

    payment_reference = models.CharField(max_length=100, unique=True)
