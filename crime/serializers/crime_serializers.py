from rest_framework import serializers

from crime.models import Crime


class CrimeSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Crime
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class CrimeDetailSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Crime
        fields = "__all__"
        read_only_fields = ("id", "created_at")
