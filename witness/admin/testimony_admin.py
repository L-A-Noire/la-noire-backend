from django.contrib import admin
from witness.models.testimony import Testimony


@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
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
        "transcription",
        "created_by__username",
    )
    readonly_fields = ("created_at",)
