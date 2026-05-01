from rest_framework import viewsets

from users.models import User
from users.permissions import AuditLogPermission, IncidentPermission, InterventionPermission

from .models import AuditLog, Incident, Intervention
from .serializers import (
    AuditLogSerializer,
    IncidentSerializer,
    InterventionSerializer,
    TechnicianInterventionSerializer,
)
from .utils import (
    apply_incident_create_rules,
    apply_incident_update_rules,
    apply_intervention_create_rules,
    apply_intervention_update_rules,
    create_audit_log,
    visible_incidents_for,
    visible_interventions_for,
)


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [IncidentPermission]

    def get_queryset(self):
        return visible_incidents_for(self.request.user)

    def perform_create(self, serializer):
        extra_kwargs = {}
        if self.request.user.role == User.Role.OPERATEUR:
            extra_kwargs["operator"] = self.request.user
        incident = serializer.save(**extra_kwargs)
        apply_incident_create_rules(incident)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Incident",
            object_id=incident.pk,
            details={"code": incident.code, "title": incident.title},
        )

    def perform_update(self, serializer):
        incident = serializer.save()
        apply_incident_update_rules(incident)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Incident",
            object_id=incident.pk,
            details={"code": incident.code, "title": incident.title},
        )

    def perform_destroy(self, instance):
        create_audit_log(
            user=self.request.user,
            action="delete",
            model_name="Incident",
            object_id=instance.pk,
            details={"code": instance.code, "title": instance.title},
        )
        instance.delete()


class InterventionViewSet(viewsets.ModelViewSet):
    permission_classes = [InterventionPermission]

    def get_queryset(self):
        return visible_interventions_for(self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.role == User.Role.TECHNICIEN and self.action in [
            "update",
            "partial_update",
        ]:
            return TechnicianInterventionSerializer
        return InterventionSerializer

    def perform_create(self, serializer):
        intervention = serializer.save()
        apply_intervention_create_rules(intervention)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Intervention",
            object_id=intervention.pk,
            details={"code": intervention.code, "description": intervention.description},
        )

    def perform_update(self, serializer):
        intervention = serializer.save()
        apply_intervention_update_rules(intervention)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Intervention",
            object_id=intervention.pk,
            details={"code": intervention.code, "description": intervention.description},
        )

    def perform_destroy(self, instance):
        create_audit_log(
            user=self.request.user,
            action="delete",
            model_name="Intervention",
            object_id=instance.pk,
            details={"code": instance.code, "description": instance.description},
        )
        instance.delete()


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogPermission]
