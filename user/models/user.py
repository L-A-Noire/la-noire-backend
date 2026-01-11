from django.contrib.auth.models import AbstractUser
from django.db import models


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

    # ToDo: add constraint for existence of at least one of the identifiers
