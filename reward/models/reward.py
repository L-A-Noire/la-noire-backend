from django.db import models
import uuid


class Reward(models.Model):
    unique_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    is_claimed = models.BooleanField(default=False)

    claimed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def reward_amount(self):
        return self.report.suspect.reward_amount or 0
