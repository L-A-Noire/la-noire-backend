from django.contrib import admin
from suspect.models.suspect_crime import SuspectCrime


@admin.register(SuspectCrime)
class SuspectCrimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "suspect",
        "crime",
        "added_at",
    )
    list_filter = (
        "added_at",
    )
    search_fields = (
        "suspect__username",
        "crime__id",
    )
