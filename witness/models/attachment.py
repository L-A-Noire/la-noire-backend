from django.db import models

from user.models import User


class Attachment(models.Model):
    file = models.FileField(
        upload_to="attachments",
    )

    provided_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="attachments",
    )
