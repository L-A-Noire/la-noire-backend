from django.contrib import admin
from crime.models.complaint import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cadet",
        "police_officer",
        "case",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "cadet__username",
        "police_officer__username",
        "description",
    )
