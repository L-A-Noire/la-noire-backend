from django.contrib import admin
from detective_board.models.detective_board import DetectiveBoard


@admin.register(DetectiveBoard)
class DetectiveBoardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "detective",
    )
    search_fields = (
        "detective__username",
        "detective__email",
    )
    readonly_fields = ("detective",)
