from rest_framework import serializers

from payment.models import Transaction


class TransactionCreateSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000)
    mobile_num = serializers.CharField(max_length=15, required=False, default="")


class InitiatePaymentResponseSerializer(serializers.Serializer):
    gateway_url = serializers.URLField()


class PaymentErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = (
            "id",
            "factor_id",
            "trans_id",
            "id_get",
            "card_number",
            "is_success",
            "created_at",
            "updated_at",
        )
