from django.db import models


class Crime(models.Model):
    LEVEL_CHOICES = (
        ("0", "critical"),
        ("1", "level_1"),
        ("2", "level_2"),
        ("3", "level_3"),
    )

    level = models.CharField(max_length=50)
