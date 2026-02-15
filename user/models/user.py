from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=100,
        null=True,
        blank=True,
    )

    password = models.CharField(
        max_length=200,
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        unique=True,
        max_length=20,
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    national_id = models.CharField(
        unique=True,
        max_length=20,
        null=True,
        blank=True,
    )

    role = models.ForeignKey(
        to="Role",
        on_delete=models.PROTECT,
    )

    # add constraint for existence of at least one of the identifiers
    def clean(self):
        if not any([self.username, self.email, self.phone, self.national_id]):
            raise ValidationError(
                "At least one of username, email, phone, or national_id must be provided")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
