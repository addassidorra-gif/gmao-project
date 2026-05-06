from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from equipment.models import Equipement
from users.models import User

from .models import AuditLog, Incident, Intervention


LEGACY_PRIORITY_VALUES = {
    "Urgente": Incident.Priority.URGENT,
    "Normale": Incident.Priority.NORMAL,
    "Faible": Incident.Priority.NORMAL,
    "Pas urgente": Incident.Priority.NORMAL,
}

LEGACY_CRITICALITY_VALUES = {
    "Haute": Equipement.Criticality.ELEVEE,
}


def normalize_legacy_choice_values(data):
    if not hasattr(data, "copy"):
        return data
    normalized = data.copy()
    if normalized.get("priority") in LEGACY_PRIORITY_VALUES:
        normalized["priority"] = LEGACY_PRIORITY_VALUES[normalized["priority"]]
    if normalized.get("criticality") in LEGACY_CRITICALITY_VALUES:
        normalized["criticality"] = LEGACY_CRITICALITY_VALUES[normalized["criticality"]]
    return normalized


class IncidentSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_code = serializers.CharField(source="equipment.code", read_only=True)
    technician_name = serializers.CharField(source="technician.full_name", read_only=True)
    technician_display_id = serializers.CharField(source="technician.display_id", read_only=True)
    operator_name = serializers.CharField(source="operator.full_name", read_only=True)
    operator_display_id = serializers.CharField(source="operator.display_id", read_only=True)

    class Meta:
        model = Incident
        fields = [
            "id",
            "code",
            "equipment",
            "equipment_name",
            "equipment_code",
            "operator",
            "operator_name",
            "operator_display_id",
            "technician",
            "technician_name",
            "technician_display_id",
            "title",
            "description",
            "criticality",
            "priority",
            "status",
            "reported_at",
            "resolved_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "resolved_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError("Le titre doit contenir au moins 4 caractères.")
        return value

    def to_internal_value(self, data):
        return super().to_internal_value(normalize_legacy_choice_values(data))

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 8:
            raise serializers.ValidationError("La description doit contenir au moins 8 caractères.")
        return value

    def validate_technician(self, value):
        if value and value.role != User.Role.TECHNICIEN:
            raise serializers.ValidationError("L'utilisateur choisi doit être un technicien.")
        if value and not value.is_active:
            raise serializers.ValidationError("Le technicien sélectionné doit être actif.")
        return value

    def validate_operator(self, value):
        if value and value.role != User.Role.OPERATEUR:
            raise serializers.ValidationError("L'utilisateur choisi doit être un opérateur.")
        if value and not value.is_active:
            raise serializers.ValidationError("L'opérateur sélectionné doit être actif.")
        return value

    def validate_reported_at(self, value):
        if value and value > timezone.now() + timedelta(days=1):
            raise serializers.ValidationError("La date de signalement ne peut pas être trop loin dans le futur.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("equipment") and not getattr(self.instance, "equipment", None):
            raise serializers.ValidationError({"equipment": "L'équipement est obligatoire."})
        if not attrs.get("technician") and not getattr(self.instance, "technician", None):
            raise serializers.ValidationError({"technician": "Le technicien est obligatoire."})
        return attrs


class InterventionSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_code = serializers.CharField(source="equipment.code", read_only=True)
    technician_name = serializers.CharField(source="technician.full_name", read_only=True)
    technician_display_id = serializers.CharField(source="technician.display_id", read_only=True)
    incident_code = serializers.CharField(source="incident.code", read_only=True)

    class Meta:
        model = Intervention
        fields = [
            "id",
            "code",
            "incident",
            "incident_code",
            "equipment",
            "equipment_name",
            "equipment_code",
            "technician",
            "technician_name",
            "technician_display_id",
            "intervention_type",
            "priority",
            "status",
            "description",
            "report",
            "start_date",
            "end_date",
            "next_maintenance",
            "equipment_status_after",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]

    def to_internal_value(self, data):
        return super().to_internal_value(normalize_legacy_choice_values(data))

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 8:
            raise serializers.ValidationError("La description doit contenir au moins 8 caractères.")
        return value

    def validate_technician(self, value):
        if value.role != User.Role.TECHNICIEN:
            raise serializers.ValidationError("L'utilisateur choisi doit être un technicien.")
        if not value.is_active:
            raise serializers.ValidationError("Le technicien sélectionné doit être actif.")
        return value

    def validate(self, attrs):
        incident = attrs.get("incident") or getattr(self.instance, "incident", None)
        equipment = attrs.get("equipment") or getattr(self.instance, "equipment", None)
        start_date = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end_date = attrs.get("end_date") if "end_date" in attrs else getattr(self.instance, "end_date", None)
        next_maintenance = attrs.get("next_maintenance") if "next_maintenance" in attrs else getattr(self.instance, "next_maintenance", None)
        status_value = attrs.get("status") or getattr(self.instance, "status", None)
        equipment_status_after = attrs.get("equipment_status_after") if "equipment_status_after" in attrs else getattr(self.instance, "equipment_status_after", None)

        if incident and equipment and incident.equipment_id != equipment.id:
            raise serializers.ValidationError({"equipment": "L'équipement doit correspondre à la panne liée."})
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "La date de fin doit être postérieure à la date de début."})
        if next_maintenance and start_date and next_maintenance < start_date:
            raise serializers.ValidationError({"next_maintenance": "La prochaine maintenance doit être postérieure à la date de début."})
        if status_value == Intervention.Status.TERMINEE and not equipment_status_after:
            raise serializers.ValidationError({"equipment_status_after": "Le statut final de l'équipement est obligatoire."})
        return attrs


class TechnicianInterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ["status", "report", "end_date", "next_maintenance", "equipment_status_after"]

    def validate_report(self, value):
        value = value.strip()
        status_value = self.initial_data.get("status") or getattr(self.instance, "status", None)
        if not value and status_value != Intervention.Status.TERMINEE:
            return value
        if len(value) < 5:
            raise serializers.ValidationError("Le rapport doit contenir au moins 5 caractères.")
        return value

    def validate(self, attrs):
        status_value = attrs.get("status") or getattr(self.instance, "status", None)
        equipment_status_after = attrs.get("equipment_status_after") if "equipment_status_after" in attrs else getattr(self.instance, "equipment_status_after", None)
        if status_value == Intervention.Status.TERMINEE and not equipment_status_after:
            raise serializers.ValidationError({"equipment_status_after": "Le statut final de l'équipement est obligatoire."})
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "action",
            "model_name",
            "object_id",
            "details",
            "created_at",
        ]
