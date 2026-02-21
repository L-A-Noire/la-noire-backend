from django.contrib import admin
from crime.models.case_report import CaseReport


@admin.register(CaseReport)
class CaseReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "case",
        "status",
        "reported_at",
    )
    list_filter = (
        "status",
        "reported_at",
    )
    search_fields = (
        "reporter__username",
        "case__id",
        "description",
    )
