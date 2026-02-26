from django.urls import include, path
from rest_framework.routers import DefaultRouter

from crime.views.case_count_views import CasesCountAPIView
from crime.views.case_report_views import CaseReportReviewView, CaseReportViewSet
from crime.views.case_views import CaseViewSet
from crime.views.complaint_views import (
    ComplaintCreateCaseView,
    ComplaintReviewByCadetView,
    ComplaintReviewByOfficerView,
    ComplaintViewSet,
)
from crime.views.crime_scene_views import CrimeSceneViewSet
from crime.views.crime_views import CrimeViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"complaints", ComplaintViewSet, basename="complaint")
router.register(r"crime-scenes", CrimeSceneViewSet, basename="crime-scene")
router.register(r"crimes", CrimeViewSet, basename="crime")
router.register(r"cases", CaseViewSet, basename="case")
router.register(r"case-reports", CaseReportViewSet, basename="case-report")

urlpatterns = [
    path("", include(router.urls)),
    # Complaint endpoints
    path(
        "complaints/<int:pk>/review-cadet/",
        ComplaintReviewByCadetView.as_view(),
        name="complaint-review-cadet",
    ),
    path(
        "complaints/<int:pk>/review-officer/",
        ComplaintReviewByOfficerView.as_view(),
        name="complaint-review-officer",
    ),
    path(
        "complaints/<int:pk>/create-case/",
        ComplaintCreateCaseView.as_view(),
        name="complaint-create-case",
    ),
    # Case report endpoints
    path(
        "case-reports/<int:pk>/review/",
        CaseReportReviewView.as_view(),
        name="case-report-review",
    ),
    path(
        "cases-count/",
        CasesCountAPIView.as_view(),
        name="cases-count",
    ),
]
