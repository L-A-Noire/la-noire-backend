from django.contrib import admin

from crime.models.case import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "crime",
        "detective",
        "is_from_crime_scene",
        "is_closed",
        "created_at",
    )
    list_filter = (
        "is_from_crime_scene",
        "is_closed",
        "created_at",
    )
    search_fields = (
        "crime__title",
        "detective__username",
    )
