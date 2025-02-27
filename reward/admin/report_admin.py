from django.contrib import admin

from reward.models.report import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "case",
        "suspect",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "reporter__username",
        "case__id",
        "suspect__suspect__username",
        "description",
    )
    readonly_fields = ("created_at",)
