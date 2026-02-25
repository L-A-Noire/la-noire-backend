from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from crime.models import CrimeScene
from .models import (
    Attachment,
    BiologicalEvidence,
    IdentificationEvidence,
    Image,
    OtherEvidence,
    Testimony,
    VehicleEvidence, Evidence,
)
from .serializers import (
    AttachmentSerializer,
    BiologicalEvidenceSerializer,
    CrimeLevelSerializer,
    EvidenceSerializer,
    IdentificationEvidenceSerializer,
    ImageSerializer,
    OtherEvidenceSerializer,
    TestimonySerializer,
    VehicleEvidenceSerializer,
)


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class BiologicalEvidenceViewSet(viewsets.ModelViewSet):
    queryset = BiologicalEvidence.objects.all()
    serializer_class = BiologicalEvidenceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class IdentificationEvidenceViewSet(viewsets.ModelViewSet):
    queryset = IdentificationEvidence.objects.all()
    serializer_class = IdentificationEvidenceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OtherEvidenceViewSet(viewsets.ModelViewSet):
    queryset = OtherEvidence.objects.all()
    serializer_class = OtherEvidenceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TestimonyViewSet(viewsets.ModelViewSet):
    queryset = Testimony.objects.all()

    def get_serializer_class(self):
        if self.action == 'confirm':
            return CrimeLevelSerializer
        return TestimonySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['POST'])
    def confirm(self, request, pk):
        if request.user.role.title not in [
            "Chief",
            "Captain",
            "Sergent",
            "Detective",
            "Police/Patrol Officer",
        ]:
            raise PermissionDenied()
        testimony = Testimony.objects.get(pk=pk)
        testimony.is_confirmed = True
        testimony.crime_scene = CrimeScene.objects.create(
            seen_at=testimony.seen_at,
            witness=testimony.created_by,
            location=testimony.location,
            description=testimony.transcription,
            examiner=request.user,
        )
        testimony.save()

        serializer = CrimeLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crime_level = serializer.validated_data["crime_level"]

        if request.user.role == "Chief":
            testimony.crime_scene.create_case(crime_level=crime_level)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VehicleEvidenceViewSet(viewsets.ModelViewSet):
    queryset = VehicleEvidence.objects.all()
    serializer_class = VehicleEvidenceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EvidenceListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['case']
