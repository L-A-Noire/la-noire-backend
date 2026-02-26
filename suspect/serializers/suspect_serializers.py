from rest_framework import serializers

from suspect.models.suspect import Suspect


class SuspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspect
        fields = '__all__'
        read_only_fields = [
            "created_at",
            "priority_score",
            "reward_amount",
        ]
