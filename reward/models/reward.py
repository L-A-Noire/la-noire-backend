from django.db import models
import uuid


class Reward(models.Model):
    unique_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    recipient = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="rewards"
    )

    amount = models.BigIntegerField(default=0)

    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="issued_rewards"
    )
