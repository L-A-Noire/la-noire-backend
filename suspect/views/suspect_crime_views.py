from django.utils import timezone
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from suspect.models import SuspectCrime
from suspect.permissions import IsDetective, IsSergeant
from suspect.serializers import (
    SuspectCrimeCreateSerializer,
    SuspectCrimeDetailSerializer,
    SuspectCrimeSerializer,
    WantedSuspectSerializer,
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
            return SuspectCrime.objects.filter(case__detective=user)
        elif role == "Sergent":
            return SuspectCrime.objects.filter(
                case__detective__in=user.detective_cases.all()
            )
        elif role == "Judge":
            return SuspectCrime.objects.filter(status="convicted")
        else:
            return SuspectCrime.objects.none()

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsDetective]
    )
    def mark_wanted(self, request, pk=None):
        suspect_crime = self.get_object()
        suspect_crime.status = "most_wanted"
        suspect_crime.wanted_since = timezone.now()
        time_diff = timezone.now() - suspect_crime.wanted_since
        hours_wanted = time_diff.total_seconds() / 3600

        # TODO: check priority_score value
        crime_level = int(suspect_crime.crime.level)
        suspect_crime.priority_score = crime_level * hours_wanted

        suspect_crime.reward_amount = suspect_crime.priority_score * 20000000
        suspect_crime.save()

        return Response(
            {
                "message": "Suspect has been added to the Most Wanted list.",
                "suspect": SuspectCrimeDetailSerializer(suspect_crime).data,
            }
        )

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


class WantedSuspectsView(generics.ListAPIView):
    serializer_class = WantedSuspectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SuspectCrime.objects.filter(
            status="most_wanted",
        ).order_by("-priority_score")
