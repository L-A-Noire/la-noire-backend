from rest_framework import serializers
from crime.models import Case
from user.seiralizers import UserSerializer
from crime.serializers import CrimeSerializer


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class CaseDetailSerializer(serializers.ModelSerializer):
    detective_details = UserSerializer(source='detective', read_only=True)
    crime_details = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def get_crime_details(self, obj):
        if obj.crime:
            return CrimeSerializer(obj.crime).data
        return None


class CaseListSerializer(serializers.ModelSerializer):
    detective_name = serializers.CharField(
        source='detective.get_full_name', read_only=True)
    crime_title = serializers.CharField(source='crime.title', read_only=True)

    class Meta:
        model = Case
        fields = ('id', 'created_at', 'is_from_crime_scene', 'is_closed',
                  'detective_name', 'crime_title')
