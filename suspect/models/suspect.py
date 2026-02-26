from django.db import models
from django.db.models import Max
from django.utils import timezone

from user.models import User


class Suspect(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='suspect',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ("wanted", "Wanted"),
        ("most_wanted", "Most Wanted"),
        ("arrested", "Arrested"),
        ("convicted", "Convicted"),
        ("innocent", "Innocent"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="wanted",
    )

    priority_score = models.IntegerField(default=0)

    reward_amount = models.BigIntegerField(default=0)

    def calculate_days_wanted(self):
        if self.status not in ["wanted", "most_wanted"]:
            return 0
        return (timezone.now() - self.created_at).days

    def update_priority_score(self):
        days = self.calculate_days_wanted()
        level_value = self.suspected_crimes.all().annotate(
            max_level=Max("crime__level")
        )["max_level"]

        self.priority_score = days * level_value
        self.reward_amount = self.priority_score * 20000000

        if days >= 30 and self.status == "wanted":
            self.status = "most_wanted"

    def save(self, *args, **kwargs):
        self.update_priority_score()
        super().save(*args, **kwargs)
