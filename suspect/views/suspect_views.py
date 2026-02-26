from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from suspect.models.suspect import Suspect
from suspect.serializers.suspect_serializers import SuspectSerializer


class SuspectModelViewSet(viewsets.ModelViewSet):
    serializer_class = SuspectSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {
        "status": ["exact", "in"],
    }

    def get_queryset(self):
        for suspect in Suspect.objects.all():
            suspect.save()
        return Suspect.objects.all()

    def perform_create(self, serializer):
        if self.request.user.role.title != "Detective":
            return PermissionDenied(detail="You can't create suspects")
        super().perform_create(serializer)

    @action(detail=True, methods=["post"])
    def mark_as_wanted(self, request, pk=None):
        if request.user.role.title != "Sergent":
            return PermissionDenied(detail="You can't mark as wanted")
        suspect = self.get_object()
        if suspect.status in [
            "suspected",
            "innocent",
        ]:
            suspect.status = "wanted"
            suspect.wanted_since = timezone.now()
            suspect.save()
