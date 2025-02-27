from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from suspect.models.suspect import Suspect
from suspect.serializers.suspect_serializers import SuspectSerializer


class SuspectModelViewSet(viewsets.ModelViewSet):
    serializer_class = SuspectSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {
        "status": ["exact", "in"],
        "suspected_crimes__crime__case__id": ["exact"],
    }

    def get_queryset(self):
        for suspect in Suspect.objects.all():
            suspect.save()
        return Suspect.objects.all()

    def perform_create(self, serializer):
        if self.request.user.role.title != "Detective":
            raise PermissionDenied(detail="You can't create suspects")
        super().perform_create(serializer)

    @action(detail=True, methods=["post"])
    def mark_as_wanted(self, request, pk=None):
        if request.user.role.title != "Sergent":
            raise PermissionDenied(detail="You can't mark as wanted")
        suspect = self.get_object()
        if suspect.status in [
            "suspected",
            "innocent",
        ]:
            suspect.status = "wanted"
            suspect.wanted_since = timezone.now()
            suspect.save()

            serializer = self.get_serializer(suspect)
            return Response(
                {
                    "message": "Suspect marked as wanted successfully",
                    "suspect": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "error": f"Cannot mark suspect with status '{suspect.status}' as wanted"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
