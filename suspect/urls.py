from django.urls import include, path
from rest_framework.routers import DefaultRouter

from suspect.views import (
    InterrogationViewSet,
    IssuePunishmentView,
    ProcessPaymentView,
    PunishmentViewSet,
    ReviewInterrogationView,
    SubmitScoreView,
    SuspectCrimeViewSet,
)
from suspect.views.suspect_views import SuspectModelViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"suspect-crimes", SuspectCrimeViewSet, basename="suspect-crime")
router.register(r"interrogations", InterrogationViewSet, basename="interrogation")
router.register(r"punishments", PunishmentViewSet, basename="punishment")
router.register("suspects", SuspectModelViewSet, basename="suspect")

urlpatterns = [
    path("", include(router.urls)),
    # Interrogation
    path(
        "interrogations/<int:pk>/submit-score/",
        SubmitScoreView.as_view(),
        name="submit-score",
    ),
    path(
        "interrogations/<int:pk>/review/",
        ReviewInterrogationView.as_view(),
        name="review-interrogation",
    ),
    # Punishment
    path(
        "suspect-crimes/<int:suspect_crime_id>/issue-punishment/",
        IssuePunishmentView.as_view(),
        name="issue-punishment",
    ),
    path(
        "punishments/<int:pk>/process-payment/",
        ProcessPaymentView.as_view(),
        name="process-payment",
    ),
]
