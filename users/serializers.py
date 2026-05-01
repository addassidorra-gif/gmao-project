import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    initials = serializers.CharField(read_only=True)
    status_label = serializers.CharField(read_only=True)
    display_id = serializers.CharField(read_only=True)
    role_label = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "is_active",
            "is_staff",
            "initials",
            "display_id",
            "status_label",
            "role_label",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "is_staff", "initials", "status_label", "date_joined"]

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("L'adresse email est obligatoire.")
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Le nom complet doit contenir au moins 3 caractères.")
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", value):
            raise serializers.ValidationError("Le nom complet contient des caractères invalides.")
        return value

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PublicUserSerializer(serializers.ModelSerializer):
    initials = serializers.CharField(read_only=True)
    status_label = serializers.CharField(read_only=True)
    display_id = serializers.CharField(read_only=True)
    role_label = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "display_id", "full_name", "role", "role_label", "is_active", "status_label", "initials"]


class MeSerializer(serializers.ModelSerializer):
    initials = serializers.CharField(read_only=True)
    status_label = serializers.CharField(read_only=True)
    display_id = serializers.CharField(read_only=True)
    role_label = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "display_id", "email", "full_name", "role", "role_label", "is_active", "status_label", "initials", "date_joined"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["role"] = user.role
        return token

    def validate(self, attrs):
        attrs["email"] = attrs.get("email", "").strip().lower()
        data = super().validate(attrs)
        data["user"] = MeSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
