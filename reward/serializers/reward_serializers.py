from rest_framework import serializers
from reward.models import Reward
from user.seiralizers import UserSerializer


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"
        read_only_fields = ("id", "unique_code", "created_at", "is_claimed")


class RewardDetailSerializer(serializers.ModelSerializer):
    recipient_details = UserSerializer(source="recipient", read_only=True)
    created_by_details = UserSerializer(source="created_by", read_only=True)

    class Meta:
        model = Reward
        fields = "__all__"
