from rest_framework import serializers

from crime.models import Complaint
from user.models import User
from user.seiralizers import UserSerializer


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"
        read_only_fields = ("id", "created_at", "rejection_count")


class ComplaintCreateSerializer(serializers.ModelSerializer):
    complainant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=True
    )

    class Meta:
        model = Complaint
        fields = ("description", "complainant_ids")

    def validate_complainant_ids(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one complainant must be provided."
            )

        users = User.objects.filter(id__in=value)
        if len(users) != len(value):
            raise serializers.ValidationError("Some complainants were not found.")

        return value

    def create(self, validated_data):
        complainant_ids = validated_data.pop("complainant_ids")

        # Auto assign to first cadet found
        from user.models import User

        cadet = User.objects.filter(role__title="Cadet").first()
        if not cadet:
            raise serializers.ValidationError("No cadet is available in the system.")

        # Auto assign to a police officer
        officer = User.objects.filter(role__title="Police/Patrol Officer").first()
        if not officer:
            raise serializers.ValidationError(
                "No police officer is available in the system."
            )

        complaint = Complaint.objects.create(
            **validated_data,
            cadet=cadet,
            police_officer=officer,
            cadet_rejection_reason="Null",
            status="pending_cadet"
        )

        complaint.complainants.set(complainant_ids)
        return complaint


class ComplaintReviewSerializer(serializers.Serializer):
    is_confirmed = serializers.BooleanField()
    rejection_reason = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def validate(self, data):
        if not data.get("is_confirmed") and not data.get("rejection_reason"):
            raise serializers.ValidationError(
                "A rejection reason must be provided when rejecting the complaint."
            )
        return data


class ComplaintDetailSerializer(serializers.ModelSerializer):
    complainants_details = UserSerializer(
        source="complainants", many=True, read_only=True
    )
    cadet_details = UserSerializer(source="cadet", read_only=True)
    officer_details = UserSerializer(source="police_officer", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Complaint
        fields = "__all__"
