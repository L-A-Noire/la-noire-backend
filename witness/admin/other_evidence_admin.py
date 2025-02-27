from django.contrib import admin

from witness.models.other_evidence import OtherEvidence


@admin.register(OtherEvidence)
class OtherEvidenceAdmin(admin.ModelAdmin):
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
