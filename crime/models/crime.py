from django.db import models


class Crime(models.Model):
    LEVEL_CHOICES = (
        ("0", "critical"),
        ("1", "level_1"),
        ("2", "level_2"),
        ("3", "level_3"),
    )

    level = models.CharField(max_length=50)

    # optional
    title = models.CharField(max_length=200)
    description = models.TextField()
    # level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    committed_at = models.DateTimeField()
    location = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="reported_crimes",
    )
