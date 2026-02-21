from django.contrib import admin
from crime.models.crime import Crime


@admin.register(Crime)
class CrimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "level",
        "committed_at",
        "location",
        "created_at",
    )
    list_filter = (
        "level",
        "committed_at",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "location",
    )
