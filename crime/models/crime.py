from django.db import models


class Crime(models.Model):
    LEVEL_CHOICES = (
        (1, "level_3"),
        (2, "level_2"),
        (3, "level_1"),
        (4, "critical"),
    )

    level = models.IntegerField(max_length=50, choices=LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
