from rest_framework import serializers
from user.models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'title')
        read_only_fields = ('id',)


class RoleDetailSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(
        source='user_set.count', read_only=True)

    class Meta:
        model = Role
        fields = ('id', 'title', 'user_count')
