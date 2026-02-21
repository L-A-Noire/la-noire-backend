from django.contrib import admin
from crime.models.crime_scene import CrimeScene


@admin.register(CrimeScene)
class CrimeSceneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "location",
        "viewer",
        "examiner",
        "case_report",
        "is_confirmed",
        "seen_at",
    )
    list_filter = (
        "is_confirmed",
        "seen_at",
    )
    search_fields = (
        "location",
        "description",
        "viewer__username",
        "examiner__username",
    )
