from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttachmentViewSet,
    BiologicalEvidenceViewSet,
    IdentificationEvidenceViewSet,
    ImageViewSet,
    OtherEvidenceViewSet,
    TestimonyViewSet,
    VehicleEvidenceViewSet,
)

router = DefaultRouter()
router.register("attachments", AttachmentViewSet)
router.register("images", ImageViewSet)
router.register("biological-evidence", BiologicalEvidenceViewSet)
router.register("identification-evidence", IdentificationEvidenceViewSet)
router.register("other-evidence", OtherEvidenceViewSet)
router.register("testimonies", TestimonyViewSet)
router.register("vehicle-evidence", VehicleEvidenceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
