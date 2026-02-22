from django.contrib import admin
from witness.models.evidence import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_at",
        "created_by",
    )
    list_filter = ("created_at",)
    search_fields = (
        "title",
        "description",
        "created_by__username",
    )
    readonly_fields = ("created_at",)
