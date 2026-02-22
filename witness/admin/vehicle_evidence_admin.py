from django.contrib import admin
from witness.models.vehicle_evidence import VehicleEvidence


@admin.register(VehicleEvidence)
class VehicleEvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "vehicle_model",
        "color",
        "registration_plate_number",
        "serial_number",
        "created_by",
        "created_at",
    )
    list_filter = (
        "created_at",
        "vehicle_model",
        "color",
    )
    search_fields = (
        "title",
        "description",
        "vehicle_model",
        "color",
        "registration_plate_number",
        "serial_number",
        "created_by__username",
    )
    readonly_fields = ("created_at",)
