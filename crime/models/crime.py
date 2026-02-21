from django.db import models


class Crime(models.Model):
    LEVEL_CHOICES = (
        ("1", "level_1"),
        ("2", "level_2"),
        ("3", "level_3"),
        ("4", "critical"),
    )

    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    committed_at = models.DateTimeField(null=True)
    location = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
