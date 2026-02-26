from django.contrib import admin
from reward.models.reward import Reward


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unique_code",
        "is_claimed",
        "claimed_at",
        "created_at",
    )
    list_filter = (
        "is_claimed",
        "claimed_at",
        "created_at",
    )
    search_fields = (
        "unique_code",
        "recipient__username",
        "recipient__email",
        "created_by__username",
    )
    readonly_fields = (
        "unique_code",
        "created_at",
    )
