from rest_framework import serializers
from suspect.models import SuspectCrime
from user.seiralizers import UserSerializer
from crime.serializers import CrimeSerializer, CaseSerializer


class SuspectCrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = '__all__'
        read_only_fields = (
            'id', 'added_at', 'priority_score', 'reward_amount')


class SuspectCrimeDetailSerializer(serializers.ModelSerializer):
    suspect_details = UserSerializer(source='suspect', read_only=True)
    case_details = CaseSerializer(source='case', read_only=True)
    added_by_details = UserSerializer(source='added_by', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = SuspectCrime
        fields = '__all__'


class SuspectCrimeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspectCrime
        fields = ('suspect', 'case', 'status')

    def validate(self, data):
        if SuspectCrime.objects.filter(
            suspect=data['suspect'],
            case=data.get('case')
        ).exists():
            raise serializers.ValidationError(
                "This suspect has already been registered for this crime.")
        return data

    def create(self, validated_data):
        if validated_data.get('status') in ['most_wanted']:
            validated_data['wanted_since'] = validated_data.get(
                'wanted_since', None)

        return super().create(validated_data)


class WantedSuspectSerializer(serializers.ModelSerializer):
    suspect_details = UserSerializer(source='suspect', read_only=True)
    crime_level = serializers.CharField(source='crime.level', read_only=True)

    class Meta:
        model = SuspectCrime
        fields = ('id', 'suspect_details', 'crime_title', 'crime_level',
                  'status', 'wanted_since', 'priority_score', 'reward_amount')
