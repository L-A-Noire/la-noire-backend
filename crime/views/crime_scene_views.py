from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import CrimeScene
from crime.serializers import (
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

    @action(detail=True, methods=["POST"])
    def confirm(self, request, pk):
        crime_scene = self.get_object()
        serializer = CrimeLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crime_level = serializer.validated_data["crime_level"]

        if (
            request.user.role.title == "Chief"
            or request.user.role.title == "Captain"
            and crime_scene.examiner.role.title
            in [
                "Sergent",
                "Detective",
                "Police/Patrol Officer",
            ]
            or request.user.role.title == "Sergent"
            and crime_scene.examiner.role.title
            in [
                "Detective",
                "Police/Patrol Officer",
            ]
            or request.user.role.title == "Detective"
            and crime_scene.examiner.role.title == "Police/Patrol Officer"
        ):
            crime_scene.is_confirmed = True
            crime_scene.create_case(crime_level=crime_level)

        return Response(status=status.HTTP_204_NO_CONTENT)
