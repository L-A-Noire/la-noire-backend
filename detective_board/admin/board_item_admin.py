from django.contrib import admin
from detective_board.models.board_item import BoardItem


@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "board",
        "evidence",
        "x_position",
        "y_position",
    )
    list_filter = (
        "board",
        "x_position",
        "y_position",
    )
    search_fields = (
        "board__detective__username",
        "evidence__title",
    )
