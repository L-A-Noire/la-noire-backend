from django.contrib import admin
from witness.models.identification_evidence import IdentificationEvidence


@admin.register(IdentificationEvidence)
class IdentificationEvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner_first_name",
        "owner_last_name",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "title",
        "description",
        "owner_first_name",
        "owner_last_name",
        "created_by__username",
    )
    readonly_fields = ("created_at",)
