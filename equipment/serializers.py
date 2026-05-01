from rest_framework import serializers
from django.utils import timezone

from .models import Equipement


class EquipementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipement
        fields = "__all__"

    def validate_code(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Le code équipement est trop court.")
        return value

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Le nom doit contenir au moins 3 caractères.")
        return value

    def validate_purchase_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("La date d'achat ne peut pas être dans le futur.")
        return value

    def validate(self, attrs):
        attrs["name"] = attrs.get("name", "").strip()
        attrs["code"] = attrs.get("code", "").strip()
        attrs["equipment_type"] = attrs.get("equipment_type", "").strip()
        attrs["manufacturer"] = attrs.get("manufacturer", "").strip()
        attrs["reference"] = attrs.get("reference", "").strip()
        attrs["location"] = attrs.get("location", "").strip()

        if not attrs["equipment_type"]:
            raise serializers.ValidationError({"equipment_type": "Le type d'équipement est obligatoire."})
        if not attrs["location"]:
            raise serializers.ValidationError({"location": "La localisation est obligatoire."})
        return attrs
