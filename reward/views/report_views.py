from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reward.models import Report, Reward
from reward.permissions import IsBaseUser, IsDetective, IsPoliceOfficer
from reward.serializers import (
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportReviewSerializer,
    ReportSerializer,
)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return ReportCreateSerializer
        elif self.action == "retrieve":
            return ReportDetailSerializer
        return ReportSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, IsBaseUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return Report.objects.none()

        role = user.role.title

        if role == "Base User":
            return Report.objects.filter(reporter=user)
        elif role in ["Police/Patrol Officer", "Detective"]:
            if role == "Police/Patrol Officer":
                return Report.objects.filter(status="pending_officer")
            else:
                return Report.objects.filter(status="pending_detective")
        elif role in ["Administrator", "Chief", "Captain"]:
            return Report.objects.all()
        else:
            return Report.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = serializer.save(reporter=request.user)

        return Response(
            ReportDetailSerializer(report).data, status=status.HTTP_201_CREATED
        )


class OfficerReviewView(generics.UpdateAPIView):
    queryset = Report.objects.filter(status="pending_officer")
    serializer_class = ReportReviewSerializer
    permission_classes = [IsAuthenticated, IsPoliceOfficer]

    def update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_approved = serializer.validated_data["is_approved"]
        report.officer = request.user

        if is_approved:
            report.status = "pending_detective"
            message = "Report approved and forwarded to the detective."
        else:
            report.status = "rejected_by_officer"
            report.officer_rejection_reason = serializer.validated_data.get(
                "rejection_reason", ""
            )
            message = "Report rejected by officer."

        report.save()

        return Response(
            {"message": message, "report": ReportDetailSerializer(report).data}
        )


class DetectiveReviewView(generics.UpdateAPIView):
    queryset = Report.objects.filter(status="pending_detective")
    serializer_class = ReportReviewSerializer
    permission_classes = [IsAuthenticated, IsDetective]

    def update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_approved = serializer.validated_data["is_approved"]
        report.detective = request.user

        if is_approved:
            suspect_person = report.suspect
            if suspect_person and suspect_person.status == "most_wanted":
                amount = suspect_person.reward_amount
            else:
                amount = 1000000  # default amount

            reward = Reward.objects.create(
                recipient=report.reporter, amount=amount, created_by=request.user
            )

            report.reward = reward
            report.status = "approved"
            message = (
                f"Report approved successfully. " f"Tracking Code: {reward.unique_code}"
            )
        else:
            report.status = "rejected_by_detective"
            report.detective_rejection_reason = serializer.validated_data.get(
                "rejection_reason", ""
            )
            message = "Report rejected by detective."

        report.save()

        return Response(
            {"message": message, "report": ReportDetailSerializer(report).data}
        )
