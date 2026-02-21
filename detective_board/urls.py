from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DetectiveBoardViewSet,
    BoardItemViewSet,
    BoardConnectionViewSet,
)

router = DefaultRouter()
router.register("boards", DetectiveBoardViewSet)
router.register("board-items", BoardItemViewSet)
router.register("board-connections", BoardConnectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
