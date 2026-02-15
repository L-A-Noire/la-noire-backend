from rest_framework import serializers
from django.contrib.auth import authenticate
from user.models import User, Role


class UserSerializer(serializers.ModelSerializer):
    role_title = serializers.CharField(source='role.title', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'first_name',
                  'last_name', 'national_id', 'role', 'role_title')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name',
                  'last_name', 'national_id', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                "Password and password confirmation do not match.")

        if not any([data.get('username'), data.get('email'),
                   data.get('phone'), data.get('national_id')]):
            raise serializers.ValidationError(
                "At least one of username, email, phone, or national_id must be provided."
            )

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        default_role, _ = Role.objects.get_or_create(title="Regular User")

        user = User.objects.create(**validated_data, role=default_role)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Please fill in all fields.")

        user = None
        if '@' in identifier:  # email
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        elif identifier.isdigit() and len(identifier) == 10:  # national id
            try:
                user = User.objects.get(national_id=identifier)
            except User.DoesNotExist:
                pass
        elif identifier.isdigit():  # phone number
            try:
                user = User.objects.get(phone=identifier)
            except User.DoesNotExist:
                pass
        else:  # username
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                "No user found with these credentials.")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Incorrect password.")

        data['user'] = user
        return data
