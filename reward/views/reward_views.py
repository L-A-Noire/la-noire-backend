from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from reward.models import Reward
from reward.serializers import (
    RewardSerializer,
    RewardDetailSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
)
from reward.permissions import CanViewRewardInfo


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated, CanViewRewardInfo]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RewardDetailSerializer
        return RewardSerializer

    def get_queryset(self):
        user = self.request.user

        national_id = self.request.query_params.get("national_id")
        if (
            national_id
            and user.role
            and user.role.title in ["Police/Patrol Officer", "Detective"]
        ):
            from user.models import User

            try:
                recipient = User.objects.get(national_id=national_id)
                return Reward.objects.filter(recipient=recipient)
            except User.DoesNotExist:
                return Reward.objects.none()

        return Reward.objects.all()


class ClaimRewardView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated, CanViewRewardInfo]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = serializer.save()

        return Response(
            {
                "message": "Reward paid successfully.",
                "payment": PaymentSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED,
        )
