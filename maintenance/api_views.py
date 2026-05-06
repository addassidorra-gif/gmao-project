from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from users.models import User
from users.permissions import AuditLogPermission, IncidentPermission, InterventionPermission

from .models import AuditLog, Incident, Intervention
from .export_utils import export_response
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

    @action(detail=False, methods=["get"], url_path=r"export/(?P<file_format>pdf|xlsx)")
    def export(self, request, file_format=None):
        if request.user.role not in [User.Role.ADMIN, User.Role.RESPONSABLE, User.Role.OPERATEUR]:
            raise PermissionDenied("Export réservé aux rôles autorisés.")
        headers = ["Code", "Titre", "Équipement", "Technicien", "Opérateur", "Criticité", "Priorité", "Statut", "Signalée le"]
        rows = (
            [
                item.code,
                item.title,
                item.equipment.name,
                item.technician.full_name if item.technician else "",
                item.operator.full_name if item.operator else "",
                item.criticality,
                item.priority,
                item.status,
                item.reported_at,
            ]
            for item in self.get_queryset().select_related("equipment", "technician", "operator")
        )
        return export_response(file_format, "pannes", "Pannes ENIB", headers, rows)


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

    @action(detail=False, methods=["get"], url_path=r"export/(?P<file_format>pdf|xlsx)")
    def export(self, request, file_format=None):
        if request.user.role not in [User.Role.ADMIN, User.Role.RESPONSABLE, User.Role.TECHNICIEN]:
            raise PermissionDenied("Export réservé aux rôles autorisés.")
        headers = ["Code", "Équipement", "Technicien", "Type", "Priorité", "Statut", "Début", "Fin", "Rapport"]
        rows = (
            [
                item.code,
                item.equipment.name,
                item.technician.full_name,
                item.intervention_type,
                item.priority,
                item.status,
                item.start_date,
                item.end_date or "",
                item.report,
            ]
            for item in self.get_queryset().select_related("equipment", "technician")
        )
        return export_response(file_format, "interventions", "Interventions ENIB", headers, rows)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogPermission]
