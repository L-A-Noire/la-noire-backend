from django.db import models

from detective_board.models.detective_board import DetectiveBoard
from witness.models import Evidence


class BoardItem(models.Model):
    board = models.ForeignKey(
        DetectiveBoard, on_delete=models.CASCADE, related_name='items'
    )

    evidence = models.ForeignKey(
        Evidence, on_delete=models.CASCADE, related_name='items'
    )

    x_position = models.FloatField(default=0)

    y_position = models.FloatField(default=0)
