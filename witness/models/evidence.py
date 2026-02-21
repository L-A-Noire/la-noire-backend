from django.db import models

from user.models import User


class Evidence(models.Model):
    title = models.CharField(
        max_length=50,
    )

    description = models.TextField()

    created_at = models.DateTimeField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
