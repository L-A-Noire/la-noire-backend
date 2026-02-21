from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import CaseReport
from crime.permissions import IsCaptain
from crime.serializers import (
    CaseReportCreateSerializer,
    CaseReportDetailSerializer,
    CaseReportReviewSerializer,
    CaseReportSerializer,
)


class CaseReportViewSet(viewsets.ModelViewSet):
    queryset = CaseReport.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CaseReportCreateSerializer
        elif self.action == "retrieve":
            return CaseReportDetailSerializer
        return CaseReportSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return CaseReport.objects.none()

        role = user.role.title

        if role in ["Administrator", "Captain", "Chief"]:
            return CaseReport.objects.all()
        elif role == "Police/Patrol Officer":
            return CaseReport.objects.filter(reporter=user)
        elif role == "Detective":
            return CaseReport.objects.filter(case__detective=user)
        else:
            return CaseReport.objects.none()


class CaseReportReviewView(generics.UpdateAPIView):
    queryset = CaseReport.objects.filter(status="pending")
    serializer_class = CaseReportReviewSerializer
    permission_classes = [IsAuthenticated, IsCaptain]

    def update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report.status = serializer.validated_data["status"]
        report.reviewed_by = request.user

        if serializer.validated_data["status"] == "rejected":
            report.rejection_reason = serializer.validated_data.get(
                "rejection_reason", ""
            )

        report.save()

        return Response(
            {
                "message": f"{dict(CaseReport.REPORT_STATUS)[report.status]}",
                "report": CaseReportDetailSerializer(report).data,
            }
        )
