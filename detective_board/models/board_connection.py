from django.db import models

from detective_board.models.board_item import BoardItem


class BoardConnection(models.Model):
    from_item = models.ForeignKey(
        BoardItem,
        on_delete=models.CASCADE,
        related_name="outgoing_connections",
    )

    to_item = models.ForeignKey(
        BoardItem,
        on_delete=models.CASCADE,
        related_name="incoming_connections",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="prevent_self_connection",
                condition=~models.Q(from_item=models.F("to_item")),
            ),
            models.UniqueConstraint(
                fields=["from_item", "to_item"],
                name="unique_directed_connection",
            ),
        ]
