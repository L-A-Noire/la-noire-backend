from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DetectiveBoard, BoardItem, BoardConnection
from .serializers import (
    DetectiveBoardSerializer,
    BoardItemSerializer,
    BoardConnectionSerializer,
)

# -------------------------
# Detective Board
# -------------------------


class DetectiveBoardViewSet(viewsets.ModelViewSet):
    serializer_class = DetectiveBoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DetectiveBoard.objects.filter(detective=self.request.user)

    def perform_create(self, serializer):
        serializer.save(detective=self.request.user)


# -------------------------
# Board Item
# -------------------------


class BoardItemViewSet(viewsets.ModelViewSet):
    serializer_class = BoardItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BoardItem.objects.filter(board__detective=self.request.user)


# -------------------------
# Board Connection
# -------------------------


class BoardConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = BoardConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BoardConnection.objects.filter(
            from_item__board__detective=self.request.user
        )
