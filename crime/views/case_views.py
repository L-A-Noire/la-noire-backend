from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import Case
from crime.permissions import IsDetective, IsSergeant
from crime.serializers import CaseDetailSerializer, CaseListSerializer, CaseSerializer


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    permission_classes = [IsAuthenticated]

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

        if role in ["Administrator", "Chief", "Captain"]:
            return Case.objects.all()
        elif role == "Detective":
            return Case.objects.filter(detective=user)
        elif role == "Sergent":
            return Case.objects.filter(detective__in=user.detective_cases.all())
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
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSergeant]
    )
    def close_case(self, request, pk=None):
        case = self.get_object()
        case.is_closed = True
        case.save()
        return Response({"message": "Case closed successfully."})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def timeline(self, request, pk=None):
        """Case timeline (complaints, crime scenes, reports)"""
        case = self.get_object()

        data = {"complaints": [], "crime_scenes": [], "reports": []}

        complaints = case.complaints.all()
        for complaint in complaints:
            data["complaints"].append(
                {
                    "id": complaint.id,
                    "description": complaint.description,
                    "status": complaint.status,
                    "created_at": complaint.created_at,
                }
            )

        if hasattr(case, "case_report"):
            crime_scenes = case.case_report.crime_scenes.all()
            for scene in crime_scenes:
                data["crime_scenes"].append(
                    {
                        "id": scene.id,
                        "location": scene.location,
                        "seen_at": scene.seen_at,
                        "is_confirmed": scene.is_confirmed,
                    }
                )

        return Response(data)
