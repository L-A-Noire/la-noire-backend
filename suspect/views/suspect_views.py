from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from suspect.models.suspect import Suspect
from suspect.serializers.suspect_serializers import SuspectSerializer


class SuspectModelViewSet(viewsets.ModelViewSet):
    queryset = Suspect.objects.all()
    serializer_class = SuspectSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {
        "status": ["exact", "in"],
    }
