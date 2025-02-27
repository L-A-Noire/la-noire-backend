from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from suspect.models import Punishment, SuspectCrime
from suspect.permissions import IsJudge, IsSergeant
from suspect.serializers import (
    PunishmentCreateSerializer,
    PunishmentDetailSerializer,
    PunishmentSerializer,
)


class PunishmentViewSet(viewsets.ModelViewSet):
    queryset = Punishment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return PunishmentCreateSerializer
        elif self.action == "retrieve":
            return PunishmentDetailSerializer
        return PunishmentSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return Punishment.objects.none()

        role = user.role.title

        if role in ["Administrator", "Chief", "Captain", "Judge"]:
            return Punishment.objects.all()
        elif role == "Sergent":
            return Punishment.objects.filter(
                punishment_type__in=["fine", "bail"], is_paid=False
            )
        else:
            return Punishment.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role.title != "Judge":
            return Response(
                {"error": "Only a judge is allowed to issue punishments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        punishment = serializer.save(issued_by=request.user)

        punishment.suspect_crime.status = "convicted"
        punishment.suspect_crime.save()

        return Response(
            PunishmentDetailSerializer(punishment).data, status=status.HTTP_201_CREATED
        )


class IssuePunishmentView(generics.CreateAPIView):
    serializer_class = PunishmentCreateSerializer
    permission_classes = [IsAuthenticated, IsJudge]

    def post(self, request, suspect_crime_id):
        suspect_crime = get_object_or_404(SuspectCrime, id=suspect_crime_id)

        if hasattr(suspect_crime, "punishment"):
            return Response(
                {"error": "A punishment has already been issued for this suspect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        punishment = serializer.save(
            suspect_crime=suspect_crime, issued_by=request.user
        )

        return Response(
            PunishmentDetailSerializer(punishment).data, status=status.HTTP_201_CREATED
        )


class ProcessPaymentView(generics.UpdateAPIView):
    queryset = Punishment.objects.filter(
        punishment_type__in=["fine", "bail"], is_paid=False
    )
    serializer_class = PunishmentSerializer
    permission_classes = [IsAuthenticated, IsSergeant]

    def update(self, request, *args, **kwargs):
        punishment = self.get_object()

        # Mock payment processing
        # TODO: real payment
        punishment.is_paid = True
        punishment.paid_at = timezone.now()
        punishment.payment_reference = (
            f"PAY-{punishment.id}-{timezone.now().timestamp()}"
        )
        punishment.save()

        return Response(
            {
                "message": "Payment processed successfully.",
                "punishment": PunishmentDetailSerializer(punishment).data,
            }
        )
