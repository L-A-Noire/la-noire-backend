from django.contrib import admin
from suspect.models.suspect import Suspect


@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "nickname",
        "gender",
        "status",
        "priority_score",
        "reward_amount",
        "wanted_since",
        "created_at",
    )
    list_filter = ("status", "gender", "created_at")
    search_fields = ("name", "nickname", "national_id")
    readonly_fields = ("priority_score", "reward_amount", "created_at")
    raw_id_fields = ("user",)
