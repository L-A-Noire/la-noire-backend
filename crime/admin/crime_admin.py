from django.contrib import admin

from crime.models.crime import Crime


@admin.register(Crime)
class CrimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "level",
        "created_at",
    )
    list_filter = (
        "level",
        "created_at",
    )
