from django.contrib import admin
from suspect.models.punishment import Punishment


@admin.register(Punishment)
class PunishmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "punishment_type",
        "suspect_crime",
        "issued_by",
        "issued_at",
    )
    list_filter = (
        "punishment_type",
        "issued_at",
        "is_paid",
    )
    search_fields = (
        "title",
        "description",
        "suspect_crime__suspect__username",
        "issued_by__username",
    )
