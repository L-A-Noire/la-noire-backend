from rest_framework import serializers

from crime.serializers import CaseSerializer
from suspect.models import Interrogation
from user.seiralizers import UserSerializer


class InterrogationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interrogation
        fields = "__all__"
        read_only_fields = ("id", "date")


class InterrogationDetailSerializer(serializers.ModelSerializer):
    suspect_crime_details = serializers.SerializerMethodField()
    case_details = CaseSerializer(source="case", read_only=True)
    interrogators_details = UserSerializer(
        source="interrogators", many=True, read_only=True
    )
    reviewed_by_details = UserSerializer(source="reviewed_by", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Interrogation
        fields = "__all__"

    def get_suspect_crime_details(self, obj):
        from .suspect_crime_serializers import SuspectCrimeSerializer

        return SuspectCrimeSerializer(obj.suspect_crime).data


class InterrogationCreateSerializer(serializers.ModelSerializer):
    interrogator_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Interrogation
        fields = ("suspect_crime", "case", "location", "notes", "interrogator_ids")

    def validate_interrogator_ids(self, value):
        from user.models import User

        if len(value) != 2:
            raise serializers.ValidationError(
                "Exactly two interrogators (a detective and a sergeant) must be assigned."
            )

        users = User.objects.filter(id__in=value)
        if len(users) != len(value):
            raise serializers.ValidationError("Some interrogators were not found.")

        return value

    def create(self, validated_data):
        interrogator_ids = validated_data.pop("interrogator_ids")
        interrogation = Interrogation.objects.create(**validated_data)
        interrogation.interrogators.set(interrogator_ids)
        return interrogation


class ScoreSubmissionSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=10)

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Score must be between 1 and 10.")
        return value

class InterrogationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interrogation
        fields = ("suspect_crime", "case", "location", "notes")

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        
        from user.models import User
        
        opposite_role = "Sergent" if user.role.title == "Detective" else "Detective"
        
        partner = User.objects.filter(role__title=opposite_role).exclude(id=user.id).first()
        
        if not partner:
            raise serializers.ValidationError(f"No {opposite_role} available for interrogation")
        
        interrogation = Interrogation.objects.create(**validated_data)
        
        interrogation.interrogators.set([user.id, partner.id])
        
        return interrogation