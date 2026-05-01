from django.db.models import Q
from django.utils import timezone

from equipment.models import Equipement

from .models import AuditLog, Incident, Intervention


def create_audit_log(user, action, model_name, object_id, details=None):
    AuditLog.objects.create(
        user=user if user and getattr(user, "is_authenticated", False) else None,
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        details=details or {},
    )


def visible_incidents_for(user):
    queryset = Incident.objects.select_related("equipment", "operator", "technician")
    if user.is_superuser or user.role in ["admin", "responsable"]:
        return queryset
    if user.role == "technicien":
        return queryset.filter(technician=user)
    if user.role == "operateur":
        return queryset.filter(operator=user)
    return queryset.none()


def visible_interventions_for(user):
    queryset = Intervention.objects.select_related("equipment", "technician", "incident", "incident__operator")
    if user.is_superuser or user.role in ["admin", "responsable"]:
        return queryset
    if user.role == "technicien":
        return queryset.filter(technician=user)
    if user.role == "operateur":
        return queryset.filter(incident__operator=user)
    return queryset.none()


def apply_incident_create_rules(incident: Incident):
    incident.equipment.status = Equipement.Status.EN_PANNE
    incident.equipment.save(update_fields=["status", "updated_at"])


def apply_incident_update_rules(incident: Incident):
    if incident.status == Incident.Status.RESOLUE:
        if not incident.resolved_at:
            Incident.objects.filter(pk=incident.pk).update(resolved_at=timezone.now())
            incident.resolved_at = timezone.now()
        open_interventions = incident.interventions.exclude(status=Intervention.Status.TERMINEE).exists()
        if not open_interventions:
            incident.equipment.status = Equipement.Status.EN_SERVICE
            incident.equipment.save(update_fields=["status", "updated_at"])
    else:
        if incident.resolved_at:
            Incident.objects.filter(pk=incident.pk).update(resolved_at=None)
            incident.resolved_at = None
        if incident.equipment.status == Equipement.Status.EN_SERVICE:
            incident.equipment.status = Equipement.Status.EN_PANNE
            incident.equipment.save(update_fields=["status", "updated_at"])


def apply_intervention_create_rules(intervention: Intervention):
    intervention.equipment.status = Equipement.Status.EN_MAINTENANCE
    intervention.equipment.save(update_fields=["status", "updated_at"])
    if intervention.incident:
        intervention.incident.status = Incident.Status.EN_COURS
        intervention.incident.save(update_fields=["status", "updated_at"])


def apply_intervention_update_rules(intervention: Intervention):
    if intervention.status != Intervention.Status.TERMINEE:
        intervention.equipment.status = Equipement.Status.EN_MAINTENANCE
        intervention.equipment.save(update_fields=["status", "updated_at"])
        if intervention.incident and intervention.incident.status == Incident.Status.EN_ATTENTE:
            intervention.incident.status = Incident.Status.EN_COURS
            intervention.incident.save(update_fields=["status", "updated_at"])
        return

    if not intervention.end_date:
        intervention.end_date = timezone.localdate()
        intervention.save(update_fields=["end_date", "updated_at"])

    final_status = intervention.equipment_status_after or Equipement.Status.EN_SERVICE
    intervention.equipment.status = final_status
    intervention.equipment.save(update_fields=["status", "updated_at"])

    if intervention.incident:
        intervention.incident.status = (
            Incident.Status.RESOLUE
            if final_status == Equipement.Status.EN_SERVICE
            else Incident.Status.EN_COURS
        )
        intervention.incident.resolved_at = (
            timezone.now() if intervention.incident.status == Incident.Status.RESOLUE else None
        )
        intervention.incident.save(update_fields=["status", "resolved_at", "updated_at"])
