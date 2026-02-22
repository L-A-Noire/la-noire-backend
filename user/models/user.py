from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models

from user.models import Role


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        admin_role = Role.objects.get(title="Administrator")

        extra_fields["role"] = admin_role

        return self.create_user(username, email, password, **extra_fields)


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

    objects = CustomUserManager()

    # add constraint for existence of at least one of the identifiers
    def clean(self):
        if not any([self.username, self.email, self.phone, self.national_id]):
            raise ValidationError(
                "At least one of username, email, phone, or national_id must be provided"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
