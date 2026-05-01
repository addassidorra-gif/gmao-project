import csv

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from users.mixins import RoleRequiredMixin
from users.models import User

from .forms import IncidentForm, IncidentOperatorForm, InterventionForm, TechnicianInterventionForm
from .models import AuditLog, Incident, Intervention
from .utils import (
    apply_incident_create_rules,
    apply_incident_update_rules,
    apply_intervention_create_rules,
    apply_intervention_update_rules,
    create_audit_log,
    visible_incidents_for,
    visible_interventions_for,
)


class HomeRedirectView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("maintenance:dashboard")
        return redirect("users:login")


class FrontendAppView(TemplateView):
    template_name = "spa/index.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "maintenance/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidents = visible_incidents_for(self.request.user)
        interventions = visible_interventions_for(self.request.user)
        from equipment.models import Equipement

        equipment_qs = Equipement.objects.all()
        context["total_equipements"] = equipment_qs.count()
        context["equipements_en_service"] = equipment_qs.filter(status=Equipement.Status.EN_SERVICE).count()
        context["equipements_en_panne"] = equipment_qs.filter(status=Equipement.Status.EN_PANNE).count()
        context["equipements_en_maintenance"] = equipment_qs.filter(status=Equipement.Status.EN_MAINTENANCE).count()
        context["incidents_ouverts"] = incidents.exclude(status=Incident.Status.RESOLUE).count()
        context["interventions_en_cours"] = interventions.filter(status=Intervention.Status.EN_COURS).count()
        context["recent_incidents"] = incidents[:5]
        context["recent_interventions"] = interventions[:5]
        return context


class IncidentListView(RoleRequiredMixin, ListView):
    model = Incident
    template_name = "maintenance/incident_list.html"
    context_object_name = "incidents"
    allowed_roles = ["responsable", "operateur"]

    def get_queryset(self):
        queryset = visible_incidents_for(self.request.user)
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if q:
            queryset = queryset.filter(
                Q(code__icontains=q)
                | Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(equipment__name__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class IncidentCreateView(RoleRequiredMixin, CreateView):
    model = Incident
    template_name = "maintenance/incident_form.html"
    success_url = reverse_lazy("maintenance:incident_list")
    allowed_roles = ["operateur"]

    def get_form_class(self):
        if self.request.user.role == User.Role.OPERATEUR:
            return IncidentOperatorForm
        return IncidentForm

    def form_valid(self, form):
        if self.request.user.role == User.Role.OPERATEUR:
            form.instance.operator = self.request.user
        response = super().form_valid(form)
        apply_incident_create_rules(self.object)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Incident",
            object_id=self.object.pk,
            details={"code": self.object.code, "title": self.object.title},
        )
        messages.success(self.request, "Panne enregistrée avec succès.")
        return response


class IncidentUpdateView(RoleRequiredMixin, UpdateView):
    model = Incident
    template_name = "maintenance/incident_form.html"
    success_url = reverse_lazy("maintenance:incident_list")
    allowed_roles = ["responsable"]

    def test_func(self):
        incident = self.get_object()
        if self.request.user.is_superuser or self.request.user.role in ["admin", "responsable"]:
            return True
        return self.request.user.role == User.Role.OPERATEUR and incident.operator_id == self.request.user.id

    def get_form_class(self):
        if self.request.user.role == User.Role.OPERATEUR:
            return IncidentOperatorForm
        return IncidentForm

    def form_valid(self, form):
        if self.request.user.role == User.Role.OPERATEUR:
            form.instance.operator = self.request.user
        response = super().form_valid(form)
        apply_incident_update_rules(self.object)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Incident",
            object_id=self.object.pk,
            details={"code": self.object.code, "title": self.object.title},
        )
        messages.success(self.request, "Panne mise à jour.")
        return response


class IncidentDeleteView(RoleRequiredMixin, DeleteView):
    model = Incident
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("maintenance:incident_list")
    allowed_roles = ["responsable"]

    def form_valid(self, form):
        request = self.request
        self.object = self.get_object()
        create_audit_log(
            user=request.user,
            action="delete",
            model_name="Incident",
            object_id=self.object.pk,
            details={"code": self.object.code, "title": self.object.title},
        )
        messages.success(request, "Panne supprimée.")
        return super().form_valid(form)


class InterventionListView(RoleRequiredMixin, ListView):
    model = Intervention
    template_name = "maintenance/intervention_list.html"
    context_object_name = "interventions"
    allowed_roles = ["responsable", "technicien"]

    def get_queryset(self):
        queryset = visible_interventions_for(self.request.user)
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if q:
            queryset = queryset.filter(
                Q(code__icontains=q)
                | Q(description__icontains=q)
                | Q(equipment__name__icontains=q)
                | Q(technician__full_name__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class InterventionCreateView(RoleRequiredMixin, CreateView):
    model = Intervention
    form_class = InterventionForm
    template_name = "maintenance/intervention_form.html"
    success_url = reverse_lazy("maintenance:intervention_list")
    allowed_roles = ["responsable"]

    def form_valid(self, form):
        response = super().form_valid(form)
        apply_intervention_create_rules(self.object)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Intervention",
            object_id=self.object.pk,
            details={"code": self.object.code, "description": self.object.description},
        )
        messages.success(self.request, "Intervention créée avec succès.")
        return response


class InterventionUpdateView(RoleRequiredMixin, UpdateView):
    model = Intervention
    template_name = "maintenance/intervention_form.html"
    success_url = reverse_lazy("maintenance:intervention_list")
    allowed_roles = ["responsable", "technicien"]

    def test_func(self):
        intervention = self.get_object()
        if self.request.user.is_superuser or self.request.user.role in ["admin", "responsable"]:
            return True
        return self.request.user.role == User.Role.TECHNICIEN and intervention.technician_id == self.request.user.id

    def get_form_class(self):
        if self.request.user.role == User.Role.TECHNICIEN:
            return TechnicianInterventionForm
        return InterventionForm

    def form_valid(self, form):
        response = super().form_valid(form)
        apply_intervention_update_rules(self.object)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Intervention",
            object_id=self.object.pk,
            details={"code": self.object.code, "description": self.object.description},
        )
        messages.success(self.request, "Intervention mise à jour.")
        return response


class InterventionDeleteView(RoleRequiredMixin, DeleteView):
    model = Intervention
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("maintenance:intervention_list")
    allowed_roles = ["responsable"]

    def form_valid(self, form):
        request = self.request
        self.object = self.get_object()
        create_audit_log(
            user=request.user,
            action="delete",
            model_name="Intervention",
            object_id=self.object.pk,
            details={"code": self.object.code, "description": self.object.description},
        )
        messages.success(request, "Intervention supprimée.")
        return super().form_valid(form)


class AuditLogListView(RoleRequiredMixin, ListView):
    model = AuditLog
    template_name = "maintenance/audit_log_list.html"
    context_object_name = "audit_logs"
    allowed_roles = ["admin"]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("user")
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(model_name__icontains=q)
                | Q(action__icontains=q)
                | Q(object_id__icontains=q)
                | Q(user__full_name__icontains=q)
            )
        return queryset


@login_required
def export_incidents_csv(request):
    if request.user.role not in ["responsable", "operateur"]:
        return HttpResponseForbidden("Export réservé aux rôles autorisés.")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="pannes.csv"'
    writer = csv.writer(response)
    writer.writerow(["Code", "Titre", "Équipement", "Technicien", "Opérateur", "Criticité", "Priorité", "Statut"])
    for item in visible_incidents_for(request.user):
        writer.writerow(
            [
                item.code,
                item.title,
                item.equipment.name,
                item.technician.full_name if item.technician else "",
                item.operator.full_name if item.operator else "",
                item.criticality,
                item.priority,
                item.status,
            ]
        )
    return response


@login_required
def export_interventions_csv(request):
    if request.user.role not in ["responsable", "technicien"]:
        return HttpResponseForbidden("Export réservé aux rôles autorisés.")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="interventions.csv"'
    writer = csv.writer(response)
    writer.writerow(["Code", "Équipement", "Technicien", "Type", "Priorité", "Statut", "Début", "Fin"])
    for item in visible_interventions_for(request.user):
        writer.writerow(
            [
                item.code,
                item.equipment.name,
                item.technician.full_name,
                item.intervention_type,
                item.priority,
                item.status,
                item.start_date,
                item.end_date or "",
            ]
        )
    return response
