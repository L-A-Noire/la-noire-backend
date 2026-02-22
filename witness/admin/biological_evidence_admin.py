from django.contrib import admin
from witness.models.biological_evidence import BiologicalEvidence


@admin.register(BiologicalEvidence)
class BiologicalEvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "coronary",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "title",
        "description",
        "result",
        "created_by__username",
        "coronary__username",
    )
    readonly_fields = ("created_at",)
