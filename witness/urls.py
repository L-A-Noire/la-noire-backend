from rest_framework.routers import DefaultRouter

from .views import (
    AttachmentViewSet,
    BiologicalEvidenceViewSet,
    EvidenceListViewSet,
    IdentificationEvidenceViewSet,
    ImageViewSet,
    OtherEvidenceViewSet,
    TestimonyViewSet,
    VehicleEvidenceViewSet,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register("attachments", AttachmentViewSet)
router.register("images", ImageViewSet)
router.register("biological-evidence", BiologicalEvidenceViewSet)
router.register("identification-evidence", IdentificationEvidenceViewSet)
router.register("other-evidence", OtherEvidenceViewSet)
router.register("testimonies", TestimonyViewSet)
router.register("vehicle-evidence", VehicleEvidenceViewSet)
router.register("evidence", EvidenceListViewSet)

urlpatterns = router.urls
