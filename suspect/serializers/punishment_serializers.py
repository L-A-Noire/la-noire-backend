from rest_framework import serializers

from crime.serializers import CaseSerializer
from suspect.models import Punishment
from user.seiralizers import UserSerializer


class PunishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Punishment
        fields = "__all__"
        read_only_fields = (
            "id",
            "issued_at",
            "is_paid",
            "paid_at",
            "payment_reference",
        )


class PunishmentDetailSerializer(serializers.ModelSerializer):
    suspect_crime_details = serializers.SerializerMethodField()
    case_details = CaseSerializer(source="case", read_only=True)
    issued_by_details = UserSerializer(source="issued_by", read_only=True)
    punishment_type_display = serializers.CharField(
        source="get_punishment_type_display", read_only=True
    )

    class Meta:
        model = Punishment
        fields = "__all__"

    def get_suspect_crime_details(self, obj):
        from .suspect_crime_serializers import SuspectCrimeSerializer

        return SuspectCrimeSerializer(obj.suspect_crime).data


class PunishmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Punishment
        fields = (
            "suspect_crime",
            "case",
            "punishment_type",
            "title",
            "description",
            "amount",
            "duration_months",
        )

    def validate(self, data):
        if data["punishment_type"] in ["fine", "bail"] and not data.get("amount"):
            raise serializers.ValidationError(
                "Amount is required for fines or bail penalties."
            )

        if data["punishment_type"] == "imprisonment" and not data.get(
            "duration_months"
        ):
            raise serializers.ValidationError(
                "Duration in months is required for imprisonment."
            )

        return data
