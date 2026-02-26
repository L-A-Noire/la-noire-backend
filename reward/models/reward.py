import uuid

from django.db import models


class Reward(models.Model):
    unique_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    recipient = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="rewards",
        null=True,
        blank=True,
    )
    amount = models.BigIntegerField(default=0)
    created_by = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="issued_rewards",
        null=True,
        blank=True,
    )

    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def reward_amount(self):
        return self.amount
