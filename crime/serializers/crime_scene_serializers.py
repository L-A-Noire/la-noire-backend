from rest_framework import serializers
from crime.models import CrimeScene
from user.seiralizers import UserSerializer


class CrimeSceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeScene
        fields = '__all__'
        read_only_fields = ('id',)


class CrimeSceneCreateSerializer(serializers.ModelSerializer):
    witness_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = CrimeScene
        fields = ('viewer', 'location', 'description',
                  'seen_at', 'witness_ids')

    def create(self, validated_data):
        witness_ids = validated_data.pop('witness_ids', [])
        crime_scene = CrimeScene.objects.create(
            **validated_data,
            is_confirmed=False
        )

        if witness_ids:
            from user.models import User
            witnesses = User.objects.filter(id__in=witness_ids)
            crime_scene.witnesses.set(witnesses)

        return crime_scene


class CrimeSceneDetailSerializer(serializers.ModelSerializer):
    viewer_details = UserSerializer(source='viewer', read_only=True)
    examiner_details = UserSerializer(source='examiner', read_only=True)
    witnesses_details = UserSerializer(
        source='witnesses', many=True, read_only=True)

    class Meta:
        model = CrimeScene
        fields = '__all__'
