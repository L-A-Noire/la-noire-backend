from rest_framework import serializers

from crime.models import Complaint
from user.seiralizers import UserSerializer


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"
        read_only_fields = ("id", "created_at", "rejection_count")


class ComplaintCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = ("description",)

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        from user.models import User

        cadet = User.objects.filter(role__title="Cadet").first()
        if not cadet:
            raise serializers.ValidationError("No cadet is available in the system.")

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
            status="pending_cadet",
        )
        complaint.complainants.add(user)

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
