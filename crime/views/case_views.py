from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import Case, CaseReport, Complaint, CrimeScene
from crime.permissions import IsDetective, IsSergeant
from crime.serializers import CaseDetailSerializer, CaseListSerializer, CaseSerializer
from suspect.permissions import IsJudge


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_closed"]

    def get_serializer_class(self):
        if self.action == "list":
            return CaseListSerializer
        elif self.action == "retrieve":
            return CaseDetailSerializer
        return CaseSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return Case.objects.none()

        role = user.role.title

        if role in ["Administrator", "Chief", "Captain", "Sergent", "Judge"]:
            return Case.objects.all()
        elif role == "Detective":
            return Case.objects.filter(detective=user)
        elif role in ["Police/Patrol Officer", "Cadet"]:
            return Case.objects.filter(case_report__reporter=user)
        else:
            return Case.objects.none()

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsDetective]
    )
    def assign_detective(self, request, pk=None):
        case = self.get_object()
        from user.models import User

        detective_id = request.data.get("detective_id")
        if not detective_id:
            return Response(
                {"error": "detective_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            detective = User.objects.get(id=detective_id, role__title="Detective")
            case.detective = detective
            case.save()
            return Response({"message": "Detective assigned to the case successfully."})
        except User.DoesNotExist:
            return Response(
                {"error": "Detective not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated & (IsSergeant | IsJudge)],
    )
    def close_case(self, request, pk=None):
        case = self.get_object()
        case.is_closed = True
        case.save()
        return Response({"message": "Case closed successfully."})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def timeline(self, request, pk=None):
        case = self.get_object()

        assigned_detective = None
        if case.detective_id:
            assigned_detective = {
                "id": case.detective.id,
                "name": case.detective.get_full_name() or case.detective.username,
            }

        events = [
            {
                "type": "case_opened",
                "date": case.created_at,
                "assigned_detective": assigned_detective,
            },
        ]

        for complaint in Complaint.objects.filter(case=case).values(
            "id", "description", "status", "created_at"
        ):
            events.append(
                {
                    "type": "complaint",
                    "date": complaint["created_at"],
                    "id": complaint["id"],
                    "description": complaint["description"],
                    "status": complaint["status"],
                }
            )

        if case.crime_id:
            for scene in CrimeScene.objects.filter(crime=case.crime).values(
                "id", "location", "seen_at", "is_confirmed"
            ):
                events.append(
                    {
                        "type": "crime_scene",
                        "date": scene["seen_at"],
                        "id": scene["id"],
                        "location": scene["location"],
                        "is_confirmed": scene["is_confirmed"],
                    }
                )

        for report in CaseReport.objects.filter(case=case).values(
            "id", "description", "status", "reported_at"
        ):
            events.append(
                {
                    "type": "report",
                    "date": report["reported_at"],
                    "id": report["id"],
                    "description": report["description"],
                    "status": report["status"],
                }
            )

        events.sort(key=lambda e: (e["date"] is None, e["date"]))

        return Response(
            {
                "case": {
                    "opened_date": case.created_at,
                    "assigned_detective": assigned_detective,
                },
                "timeline": events,
            }
        )
