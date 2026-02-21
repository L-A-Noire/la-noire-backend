from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from crime.models import Crime
from crime.permissions import IsPoliceOfficer
from crime.serializers import CrimeDetailSerializer, CrimeSerializer


class CrimeViewSet(viewsets.ModelViewSet):
    queryset = Crime.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrimeDetailSerializer
        return CrimeSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsPoliceOfficer]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role and user.role.title in [
            "Administrator",
            "Chief",
            "Captain",
            "Detective",
        ]:
            return Crime.objects.all()
        elif user.role and user.role.title == "Police/Patrol Officer":
            return Crime.objects.filter(reported_by=user)
        return Crime.objects.none()
