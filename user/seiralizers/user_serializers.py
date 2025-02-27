from django.contrib.auth import authenticate
from rest_framework import serializers

from user.models import Role, User


class UserSerializer(serializers.ModelSerializer):
    role_title = serializers.CharField(source="role.title", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "national_id",
            "role",
            "role_title",
        )
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "national_id",
            "password",
        )

    def validate(self, data):
        if not any(
            [
                data.get("username"),
                data.get("email"),
                data.get("phone"),
                data.get("national_id"),
            ]
        ):
            raise serializers.ValidationError(
                "At least one of username, email, phone, or national_id must be provided."
            )

        return data

    def create(self, validated_data):
        password = validated_data.pop("password")

        default_role, _ = Role.objects.get_or_create(title="Base User")

        user = User.objects.create(**validated_data, role=default_role)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            raise serializers.ValidationError("Please fill in all fields.")

        user = None
        if "@" in identifier:  # email
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
            raise serializers.ValidationError("No user found with these credentials.")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Incorrect password.")

        data["user"] = user
        return data


class UserListWithRoleSerializer(serializers.ModelSerializer):
    role_title = serializers.CharField(source="role.title", read_only=True)
    role_id = serializers.IntegerField(source="role.id", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "national_id",
            "role_id",
            "role_title",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")


class ChangeUserRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    role_id = serializers.IntegerField(required=True)

    def validate(self, data):
        user_id = data.get("user_id")
        role_id = data.get("role_id")

        try:
            user = User.objects.get(id=user_id)
            data["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found."})

        try:
            role = Role.objects.get(id=role_id)
            data["role"] = role
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role_id": "Role not found."})

        return data
