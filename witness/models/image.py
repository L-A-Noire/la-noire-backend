from django.db import models

from user.models import User


class Image(models.Model):
    image = models.ImageField(upload_to="images")

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
