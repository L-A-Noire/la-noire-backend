# reward/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from reward.views import (
    ClaimRewardAPIView,
    DetectiveReviewView,
    MyRewardsView,
    OfficerReviewView,
    ReportViewSet,
    RewardViewSet,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"rewards", RewardViewSet, basename="reward")

urlpatterns = [
    path("rewards/claim/", ClaimRewardAPIView.as_view(), name="reward-claim"),
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
    path("my-rewards/", MyRewardsView.as_view(), name="my-rewards"),
]
