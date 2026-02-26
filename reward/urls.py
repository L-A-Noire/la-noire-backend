# reward/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reward.views import (
    ReportViewSet,
    OfficerReviewView,
    DetectiveReviewView,
    RewardViewSet,
    ClaimRewardView,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"rewards", RewardViewSet, basename="reward")

urlpatterns = [
    path("", include(router.urls)),
    # Review endpoints
    path(
        "reports/<int:pk>/review-officer/",
        OfficerReviewView.as_view(),
        name="report-review-officer",
    ),
    path(
        "reports/<int:pk>/review-detective/",
        DetectiveReviewView.as_view(),
        name="report-review-detective",
    ),
    path("rewards/claim/", ClaimRewardView.as_view(), name="reward-claim"),
]
