from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.models import User
from suspect.models import SuspectCrime
from suspect.permissions import IsSergeant
from suspect.serializers import (
    SuspectCrimeCreateSerializer,
    SuspectCrimeDetailSerializer,
    SuspectCrimeSerializer,
)


class SuspectCrimeViewSet(viewsets.ModelViewSet):
    queryset = SuspectCrime.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return SuspectCrimeCreateSerializer
        elif self.action == "retrieve":
            return SuspectCrimeDetailSerializer
        return SuspectCrimeSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return SuspectCrime.objects.none()

        role = user.role.title

        if role in ["Administrator", "Chief", "Captain"]:
            return SuspectCrime.objects.all()
        elif role == "Detective":
            return SuspectCrime.objects.filter(crime__case__detective=user)
        elif role == "Sergent":
            detectives_under_sergeant = User.objects.filter(
                role__title="Detective",
                detective_cases__isnull=False
            ).distinct()
            return SuspectCrime.objects.filter(
                crime__case__detective__in=detectives_under_sergeant
            )
        elif role == "Judge":
            return SuspectCrime.objects.filter(status="convicted")
        else:
            return SuspectCrime.objects.none()

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSergeant]
    )
    def arrest(self, request, pk=None):
        suspect_crime = self.get_object()

        suspect_crime.status = "arrested"
        suspect_crime.wanted_until = timezone.now()
        suspect_crime.save()

        return Response(
            {
                "message": "Suspect has been arrested.",
                "suspect": SuspectCrimeDetailSerializer(suspect_crime).data,
            }
        )
