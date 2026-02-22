from django.contrib import admin
from reward.models.reporter import Reporter


@admin.register(Reporter)
class ReporterAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ()
