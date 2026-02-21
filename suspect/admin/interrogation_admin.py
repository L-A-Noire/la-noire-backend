from django.contrib import admin
from suspect.models.interrogation import Interrogation


@admin.register(Interrogation)
class InterrogationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "suspect_crime",
        "case",
        "date",
        "location",
        "final_score",
    )
    list_filter = ("date",)
    search_fields = (
        "suspect_crime__suspect__username",
        "case__id",
        "location",
        "notes",
    )
