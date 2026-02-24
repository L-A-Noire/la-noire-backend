from datetime import timezone
from django.db import models

from crime.models import Case


class SuspectCrime(models.Model):
    suspect = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="suspected_crimes"
    )

    case = models.ForeignKey(
        to=Case,
        on_delete=models.PROTECT,
        related_name="suspects",
        null=True,
        blank=True,
    )

    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        to="user.User", on_delete=models.PROTECT, related_name="added_suspects"
    )

    STATUS_CHOICES = (
        ("suspect", "Suspect"),
        ("wanted", "Wanted"),
        ("most_wanted", "Most Wanted"),
        ("arrested", "Arrested"),
        ("convicted", "Convicted"),
        ("innocent", "Innocent"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="suspect")

    wanted_since = models.DateTimeField(null=True, blank=True)
    wanted_until = models.DateTimeField(null=True, blank=True)

    priority_score = models.IntegerField(default=0)

    reward_amount = models.BigIntegerField(default=0)

    def calculate_days_wanted(self):
        if not self.wanted_since:
            return 0
        
        end_date = self.wanted_until or timezone.now()
        delta = end_date - self.wanted_since
        return delta.days
    
    def get_crime_level_value(self):
        level_map = {
            "critical": 4,
            "1": 3,
            "2": 2,
            "3": 1
        }
        return level_map.get(self.case.crime.level, 1)
    
    def update_priority_score(self):
        days = self.calculate_days_wanted()
        level_value = self.get_crime_level_value()
        
        self.priority_score = days * level_value
        self.reward_amount = self.priority_score * 20000000
        
        if days >= 30 and self.status == "wanted":
            self.status = "most_wanted"
        
        self.save()