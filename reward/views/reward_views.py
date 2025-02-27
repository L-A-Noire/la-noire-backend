from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reward.models import Reward
from reward.permissions import CanViewRewardInfo
from reward.serializers import (
    ClaimRewardErrorSerializer,
    ClaimRewardRequestSerializer,
    ClaimRewardResponseSerializer,
    RewardDetailSerializer,
    RewardSerializer,
)


class MyRewardsView(APIView):
    """List rewards for the current user (e.g. Base User)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        rewards = Reward.objects.filter(recipient=request.user).order_by("-created_at")
        serializer = RewardSerializer(rewards, many=True)
        return Response(serializer.data)


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
    permission_classes = [IsAuthenticated, CanViewRewardInfo]

    @extend_schema(
        summary="Claim a reward",
        description="Claim a reward by reward code and recipient national ID. "
        "Only police and authorized roles can use this endpoint. "
        "National ID must match the reward recipient.",
        request=ClaimRewardRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=ClaimRewardResponseSerializer,
                description="Reward claimed successfully",
            ),
            400: OpenApiResponse(
                response=ClaimRewardErrorSerializer,
                description="Invalid code, missing national ID, or national ID does not match recipient",
            ),
        },
        tags=["reward"],
    )
    def post(self, request):
        from user.models import User

        code = request.data.get("reward_code")
        national_id = request.data.get("national_id")

        if not code:
            return Response(
                {"detail": "Reward code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not national_id:
            return Response(
                {"detail": "National ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            recipient = User.objects.get(national_id=national_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "No user found with this national ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reward = Reward.objects.get(unique_code=code, is_claimed=False)
        except Reward.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used reward code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reward.recipient_id != recipient.id:
            return Response(
                {"detail": "National ID does not match the reward recipient."},
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
