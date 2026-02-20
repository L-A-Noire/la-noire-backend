from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from crime.models import CrimeScene, Case, CaseReport
from crime.serializers import (
    CrimeSceneSerializer, CrimeSceneCreateSerializer, CrimeSceneDetailSerializer
)
from crime.permissions import IsPoliceOfficer, IsDetective
from crime.models import CaseReport
from crime.serializers import CaseReportCreateSerializer
from crime.models import Case


class CrimeSceneViewSet(viewsets.ModelViewSet):
    queryset = CrimeScene.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrimeSceneCreateSerializer
        elif self.action == 'retrieve':
            return CrimeSceneDetailSerializer
        return CrimeSceneSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return CrimeScene.objects.none()

        if user.role.title in ['Police/Patrol Officer', 'Detective', 'Captain', 'Chief']:
            return CrimeScene.objects.all()
        elif user.role.title == 'Coronary':
            return CrimeScene.objects.filter(examiner=user)
        else:
            return CrimeScene.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crime_scene = serializer.save()

        case = Case.objects.create(
            is_from_crime_scene=True,
            is_closed=False
        )

        case_report_data = {
            'reporter': request.user.id,
            'case': case.id,
            'description': f"Crime scene at {crime_scene.location}"
        }

        case_report_serializer = CaseReportCreateSerializer(
            data=case_report_data)
        if case_report_serializer.is_valid():
            case_report = case_report_serializer.save()

            crime_scene.case_report = case_report
            crime_scene.save()

            return Response({
                "message": "Crime scene registered successfully and an initial report was created.",
                "crime_scene": CrimeSceneDetailSerializer(crime_scene).data,
                "case_id": case.id,
                "case_report_id": case_report.id
            }, status=status.HTTP_201_CREATED)
        else:
            # If case report creation fails delete the crime scene
            crime_scene.delete()
            return Response(case_report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
