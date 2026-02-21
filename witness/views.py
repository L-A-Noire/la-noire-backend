from rest_framework import viewsets
from .models import (
    Attachment,
    BiologicalEvidence,
    IdentificationEvidence,
    Image,
    OtherEvidence,
    Testimony,
    VehicleEvidence,
)
from .serializers import (
    AttachmentSerializer,
    BiologicalEvidenceSerializer,
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


class IdentificationEvidenceViewSet(viewsets.ModelViewSet):
    queryset = IdentificationEvidence.objects.all()
    serializer_class = IdentificationEvidenceSerializer


class OtherEvidenceViewSet(viewsets.ModelViewSet):
    queryset = OtherEvidence.objects.all()
    serializer_class = OtherEvidenceSerializer


class TestimonyViewSet(viewsets.ModelViewSet):
    queryset = Testimony.objects.all()
    serializer_class = TestimonySerializer


class VehicleEvidenceViewSet(viewsets.ModelViewSet):
    queryset = VehicleEvidence.objects.all()
    serializer_class = VehicleEvidenceSerializer