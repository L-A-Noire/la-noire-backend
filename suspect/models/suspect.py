from datetime import timedelta

from django.db import models
from django.db.models import Max
from django.utils import timezone

from user.models import User


class Suspect(models.Model):
    GENDER_CHOICES = (
        ("m", "Male"),
        ("f", "Female"),
    )

    description = models.TextField()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="suspect",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)

    nickname = models.CharField(max_length=100)

    gender = models.CharField(
        max_length=100, choices=GENDER_CHOICES, null=True, blank=True
    )

    picture = models.ImageField(
        upload_to="suspect",
        null=True,
        blank=True,
    )

    national_id = models.IntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ("suspected", "Suspected"),
        ("wanted", "Wanted"),
        ("most_wanted", "Most Wanted"),
        ("arrested", "Arrested"),
        ("convicted", "Convicted"),
        ("innocent", "Innocent"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="suspected",
    )

    wanted_since = models.DateTimeField(
        null=True,
        blank=True,
    )

    priority_score = models.IntegerField(default=0)

    reward_amount = models.BigIntegerField(default=0)

    def calculate_days_wanted(self):
        if self.status not in ["wanted", "most_wanted"]:
            return 0
        return (timezone.now() - self.wanted_since).days

    def update_priority_score(self):
        days = self.calculate_days_wanted()
        level_value = self.suspected_crimes.all().annotate(
            max_level=Max("crime__level")
        )["max_level"]

        self.priority_score = days * level_value
        self.reward_amount = self.priority_score * 20000000

    def mark_as_most_wanted_if_necessary(self):
        if (
            self.status == "wanted"
            and self.wanted_since.date() < timezone.now() - timedelta(days=30)
        ):
            self.status = "most_wanted"

    def save(self, *args, **kwargs):
        if self.pk:
            self.update_priority_score()
            self.mark_as_most_wanted_if_necessary()
        super().save(*args, **kwargs)
