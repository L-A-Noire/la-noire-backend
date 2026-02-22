from django.contrib import admin
from detective_board.models.board_connection import BoardConnection


@admin.register(BoardConnection)
class BoardConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "from_item",
        "to_item",
    )
    search_fields = (
        "from_item__board__detective__username",
        "to_item__board__detective__username",
        "from_item__evidence__title",
        "to_item__evidence__title",
    )
