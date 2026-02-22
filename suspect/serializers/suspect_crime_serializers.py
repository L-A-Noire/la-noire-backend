from rest_framework import serializers

from crime.serializers import CaseSerializer
from suspect.models import SuspectCrime
from user.seiralizers import UserSerializer


class SuspectCrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = "__all__"
        read_only_fields = ("id", "added_at", "priority_score", "reward_amount")


class SuspectCrimeDetailSerializer(serializers.ModelSerializer):
    suspect_details = UserSerializer(source="suspect", read_only=True)
    case_details = CaseSerializer(source="case", read_only=True)
    added_by_details = UserSerializer(source="added_by", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SuspectCrime
        fields = "__all__"


class SuspectCrimeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = ("suspect", "case", "status")

    def validate(self, data):
        if SuspectCrime.objects.filter(
            suspect=data["suspect"], case=data.get("case")
        ).exists():
            raise serializers.ValidationError(
                "This suspect has already been registered for this crime."
            )
        return data

    def create(self, validated_data):
        if validated_data.get("status") in ["wanted","most_wanted"]:
            validated_data["wanted_since"] = validated_data.get("wanted_since", None)

        return super().create(validated_data)


class WantedSuspectSerializer(serializers.ModelSerializer):
    suspect_details = UserSerializer(source="suspect", read_only=True)
    crime_level = serializers.CharField(source="crime.level", read_only=True)
    crime_title = serializers.CharField(source="crime.title", read_only=True)
    crime_level_display = serializers.CharField(source='crime.get_level_display', read_only=True)
    days_wanted = serializers.SerializerMethodField()

    class Meta:
        model = SuspectCrime
        fields = (
            "id",
            "suspect_details",
            "crime_title",
            "crime_level",
            "crime_level_display"
            "status",
            "wanted_since",
            "days_wanted",
            "priority_score",
            "reward_amount",
        )
    
    def get_days_wanted(self, obj):
        return obj.calculate_days_wanted()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if data.get('reward_amount'):
            data['reward_amount_formatted'] = f"{data['reward_amount']:,}"
        
        days = data.get('days_wanted', 0)
        if days >= 30:
            months = days // 30
            remaining_days = days % 30
            data['wanted_duration'] = f"{months} months & {remaining_days} days"
        else:
            data['wanted_duration'] = f"{days} days"
        
        return data
