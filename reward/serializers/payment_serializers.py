from datetime import timezone
from rest_framework import serializers
from reward.models import Payment, Reward


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "processed_at", "payment_reference")


class PaymentCreateSerializer(serializers.Serializer):
    unique_code = serializers.UUIDField()
    national_id = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=200)

    def validate(self, data):
        try:
            reward = Reward.objects.get(
                unique_code=data["unique_code"], is_claimed=False
            )
        except Reward.DoesNotExist:
            raise serializers.ValidationError("Invalid or already claimed reward code")

        self.context["reward"] = reward
        return data

    def create(self, validated_data):
        reward = self.context["reward"]

        reward.is_claimed = True
        reward.claimed_at = timezone.now()
        reward.save()

        payment = Payment.objects.create(
            reward=reward,
            processed_by=self.context["request"].user,
            recipient_national_id=validated_data["national_id"],
            recipient_full_name=validated_data["full_name"],
            payment_reference=f"PAY-{reward.unique_code}-{timezone.now().timestamp()}",
        )

        return payment
