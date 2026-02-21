from rest_framework import serializers
from .models import (
    Attachment,
    BiologicalEvidence,
    IdentificationEvidence,
    Image,
    OtherEvidence,
    Testimony,
    VehicleEvidence,
)


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        read_only_fields = ("id",)


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class BiologicalEvidenceSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(),
        many=True,
    )

    class Meta:
        model = BiologicalEvidence
        fields = "__all__"


class IdentificationEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentificationEvidence
        fields = "__all__"


class OtherEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherEvidence
        fields = "__all__"


class TestimonySerializer(serializers.ModelSerializer):
    attachments = serializers.PrimaryKeyRelatedField(
        queryset=Attachment.objects.all(),
        many=True,
    )

    class Meta:
        model = Testimony
        fields = "__all__"


class VehicleEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleEvidence
        fields = "__all__"

    def validate(self, attrs):
        serial = attrs.get("serial_number")
        plate = attrs.get("registration_plate_number")

        if bool(serial) == bool(plate):
            raise serializers.ValidationError(
                "Exactly one of serial_number or registration_plate_number must be provided."
            )

        return attrs
