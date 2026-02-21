from django.db import models
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from user.models import User


class DetectiveBoard(models.Model):
    detective = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="detective_board",
    )

    def are_connected(self, item1, item2):
        from detective_board.models.board_connection import BoardConnection
        if item1.board != self or item2.board != self:
            raise ValidationError("Items do not belong to this board")
        return BoardConnection.objects.filter(
            Q(from_item=item1, to_item=item2) |
            Q(from_item=item2, to_item=item1)
        ).exists()
