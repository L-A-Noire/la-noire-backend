from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from reward.models import Reward
from reward.serializers import (
    RewardSerializer,
    RewardDetailSerializer,
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
                return Reward.objects.filter(recipient=recipient, is_claimed=False)
            except User.DoesNotExist:
                return Reward.objects.none()

        return Reward.objects.all()


class ClaimRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("reward_code")

        if not code:
            return Response(
                {"detail": "Reward code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reward = Reward.objects.get(unique_code=code, is_claimed=False)
        except Reward.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used reward code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reward.is_claimed = True
        reward.claimed_at = timezone.now()
        reward.save()

        return Response(
            {
                "detail": "Reward claimed successfully.",
                "amount": reward.reward_amount,
            }
        )
