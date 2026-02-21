from rest_framework import serializers
from reward.models import Report
from user.seiralizers import UserSerializer
from crime.serializers import CaseSerializer
from suspect.serializers import SuspectCrimeSerializer


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("id", "created_at", "status")


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("case", "suspect", "description")

    def validate(self, data):
        if not data.get("case") and not data.get("suspect"):
            raise serializers.ValidationError("Either case or suspect must be provided")
        return data


class ReportReviewSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get("is_approved") and not data.get("rejection_reason"):
            raise serializers.ValidationError(
                "Rejection reason is required when rejecting"
            )
        return data


class ReportDetailSerializer(serializers.ModelSerializer):
    reporter_details = UserSerializer(source="reporter", read_only=True)
    officer_details = UserSerializer(source="officer", read_only=True)
    detective_details = UserSerializer(source="detective", read_only=True)
    case_details = CaseSerializer(source="case", read_only=True)
    suspect_details = SuspectCrimeSerializer(source="suspect", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Report
        fields = "__all__"
