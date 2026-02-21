from django.contrib import admin
from suspect.models.suspect_crime import SuspectCrime


@admin.register(SuspectCrime)
class SuspectCrimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "suspect",
        "case",
        "status",
        "priority_score",
        "reward_amount",
        "added_at",
    )
    list_filter = (
        "status",
        "added_at",
        "wanted_since",
    )
    search_fields = (
        "suspect__username",
        "case__id",
    )
