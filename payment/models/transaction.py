import random

from django.db import models


def generate_factor_id():
    return str(random.randint(100000000000, 999999999999))


class Transaction(models.Model):
    factor_id = models.CharField(max_length=12, unique=True, default=generate_factor_id)
    trans_id = models.CharField(max_length=64, blank=True, null=True)
    id_get = models.CharField(max_length=64, blank=True, null=True)
    amount = models.BigIntegerField()
    mobile_num = models.CharField(max_length=15, blank=True, default="")
    description = models.CharField(max_length=255, blank=True, default="")
    card_number = models.CharField(max_length=20, blank=True, default="")
    is_success = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction {self.factor_id} - {'Success' if self.is_success else 'Pending'}"
