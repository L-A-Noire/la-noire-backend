from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import Case, CrimeScene
from crime.serializers import (
    CaseReportCreateSerializer,
    CrimeSceneCreateSerializer,
    CrimeSceneDetailSerializer,
    CrimeSceneSerializer,
)
from witness.serializers import CrimeLevelSerializer


class CrimeSceneViewSet(viewsets.ModelViewSet):
    queryset = CrimeScene.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CrimeSceneCreateSerializer
        elif self.action == "retrieve":
            return CrimeSceneDetailSerializer
        elif self.action == "confirm":
            return CrimeLevelSerializer
        return CrimeSceneSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return CrimeScene.objects.none()

        if user.role.title in [
            "Administrator",
            "Police/Patrol Officer",
            "Detective",
            "Captain",
            "Chief",
        ]:
            return CrimeScene.objects.all()
        elif user.role.title == "Coronary":
            return CrimeScene.objects.filter(examiner=user)
        else:
            return CrimeScene.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crime_scene = serializer.save()

        case = Case.objects.create(is_from_crime_scene=True, is_closed=False)

        case_report_data = {
            "reporter": request.user.id,
            "case": case.id,
            "description": f"Crime scene at {crime_scene.location}",
        }

        case_report_serializer = CaseReportCreateSerializer(data=case_report_data)
        if case_report_serializer.is_valid():
            case_report = case_report_serializer.save()

            crime_scene.case_report = case_report
            crime_scene.save()

            return Response(
                {
                    "message": "Crime scene registered successfully and an initial report was created.",
                    "crime_scene": CrimeSceneDetailSerializer(crime_scene).data,
                    "case_id": case.id,
                    "case_report_id": case_report.id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            # If case report creation fails delete the crime scene
            crime_scene.delete()
            return Response(
                case_report_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["POST"])
    def confirm(self, request):
        crime_scene = self.get_object()
        serializer = CrimeLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crime_level = serializer.validated_data["crime_level"]

        if (
            request.user.role == "Chief"
            or request.user.role == "Captain" and crime_scene.examiner.role in [
                "Sergent",
                "Detective",
                "Police/Patrol Officer",
            ]
            or request.user.role == "Sergent" and crime_scene.examiner.role in[
                "Detective",
                "Police/Patrol Officer",
            ]
            or request.user.role == "Detective" and crime_scene.examiner.role
            == "Police/Patrol Officer"
        ):
            crime_scene.create_case(crime_level=crime_level)

        return Response(status=status.HTTP_204_NO_CONTENT)
