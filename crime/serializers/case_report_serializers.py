from rest_framework import serializers

from crime.models import CaseReport
from user.seiralizers import UserSerializer


class CaseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseReport
        fields = "__all__"
        read_only_fields = ("id", "reported_at")


class CaseReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseReport
        fields = ("reporter", "case", "description")

    def create(self, validated_data):
        return CaseReport.objects.create(**validated_data, status="pending")


class CaseReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["approved", "rejected"])
    rejection_reason = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def validate(self, data):
        if data.get("status") == "rejected" and not data.get("rejection_reason"):
            raise serializers.ValidationError(
                "A rejection reason must be provided when rejecting the report."
            )
        return data


class CaseReportDetailSerializer(serializers.ModelSerializer):
    reporter_details = UserSerializer(source="reporter", read_only=True)
    reviewed_by_details = UserSerializer(source="reviewed_by", read_only=True)

    class Meta:
        model = CaseReport
        fields = "__all__"
