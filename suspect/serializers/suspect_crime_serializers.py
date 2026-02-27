from rest_framework import serializers

from crime.serializers import CaseSerializer
from suspect.models import SuspectCrime
from suspect.serializers.suspect_serializers import SuspectSerializer
from user.seiralizers import UserSerializer


class SuspectCrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = "__all__"
        read_only_fields = ("id", "added_at", "priority_score", "reward_amount")


class SuspectCrimeDetailSerializer(serializers.ModelSerializer):
    suspect_details = SuspectSerializer(source="suspect", read_only=True)
    case_details = CaseSerializer(source="case", read_only=True)
    added_by_details = UserSerializer(source="added_by", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SuspectCrime
        fields = "__all__"


class SuspectCrimeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = ("suspect", "crime")

    def validate(self, data):
        if SuspectCrime.objects.filter(
            suspect=data["suspect"], crime=data.get("crime")
        ).exists():
            raise serializers.ValidationError(
                "This suspect has already been registered for this crime."
            )
        return super().validate(data)

    def create(self, validated_data):
        request = self.context["request"]

        validated_data["added_by"] = request.user
        return super().create(validated_data)
