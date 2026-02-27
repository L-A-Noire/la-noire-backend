from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from suspect.models import Interrogation
from suspect.permissions import IsCaptain
from suspect.serializers import (
    InterrogationCreateSerializer,
    InterrogationDetailSerializer,
    InterrogationSerializer,
    ScoreSubmissionSerializer,
)


class InterrogationViewSet(viewsets.ModelViewSet):
    queryset = Interrogation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return InterrogationCreateSerializer
        elif self.action == "retrieve":
            return InterrogationDetailSerializer
        return InterrogationSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return Interrogation.objects.none()

        role = user.role.title

        if role in ["Administrator", "Captain", "Chief"]:
            return Interrogation.objects.all()
        elif role in ["Detective", "Sergent"]:
            return Interrogation.objects.filter(interrogators=user)
        elif role == "Judge":
            return Interrogation.objects.filter(case__in=user.case_set.all())
        else:
            return Interrogation.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interrogation = serializer.save()

        return Response(
            InterrogationDetailSerializer(interrogation).data,
            status=status.HTTP_201_CREATED,
        )


class SubmitScoreView(generics.UpdateAPIView):
    serializer_class = ScoreSubmissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Interrogation.objects.all()

    def update(self, request, *args, **kwargs):
        interrogation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        score = serializer.validated_data["score"]
        user = request.user

        if user.role.title == "Detective":
            interrogation.detective_score = score
            message = "Detective score has been submitted."
        elif user.role.title == "Sergent":
            interrogation.sergeant_score = score
            message = "Sergeant score has been submitted."
        else:
            return Response(
                {
                    "error": "Only detectives and sergeants are allowed to submit scores."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if interrogation.detective_score and interrogation.sergeant_score:
            message += " Both scores have been submitted. Awaiting captain review."

        interrogation.save()

        return Response(
            {
                "message": message,
                "interrogation": InterrogationDetailSerializer(interrogation).data,
            }
        )


class ReviewInterrogationView(generics.UpdateAPIView):
    serializer_class = ScoreSubmissionSerializer
    permission_classes = [IsAuthenticated, IsCaptain]
    queryset = Interrogation.objects.all()

    def update(self, request, *args, **kwargs):
        interrogation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        final_score = serializer.validated_data["score"]

        interrogation.final_score = final_score
        interrogation.reviewed_by = request.user

        suspect_crime = interrogation.suspect_crime
        suspect = suspect_crime.suspect

        if final_score >= 7:
            # Convicted
            suspect_crime.status = "convicted"
            suspect.status = "convicted"
            message = "Suspect has been convicted. Case will proceed to trial."
        elif final_score <= 3:
            # Innocent
            suspect_crime.status = "innocent"
            suspect.status = "innocent"
            message = "Suspect has been found innocent and will be released."
        else:
            # Inconclusive - keep as arrested for further investigation
            suspect_crime.status = "arrested"
            suspect.status = "arrested"
            message = "Results inconclusive. Suspect remains in custody for further investigation."

        # Save both
        suspect_crime.save()
        suspect.save()
        interrogation.save()

        return Response(
            {
                "message": message,
                "interrogation": InterrogationDetailSerializer(interrogation).data,
                "suspect_status": suspect.status,
                "suspect_crime_status": suspect_crime.status,
            }
        )
