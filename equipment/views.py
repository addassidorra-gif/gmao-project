import csv

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from maintenance.utils import create_audit_log
from users.mixins import RoleRequiredMixin

from .forms import EquipementForm
from .models import Equipement


class EquipementListView(RoleRequiredMixin, ListView):
    model = Equipement
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipements"
    allowed_roles = ["admin"]

    def get_queryset(self):
        queryset = Equipement.objects.all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if q:
            queryset = queryset.filter(
                Q(code__icontains=q)
                | Q(name__icontains=q)
                | Q(location__icontains=q)
                | Q(reference__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class EquipementCreateView(RoleRequiredMixin, CreateView):
    model = Equipement
    form_class = EquipementForm
    template_name = "equipment/equipment_form.html"
    success_url = reverse_lazy("equipment:list")
    allowed_roles = ["admin"]

    def form_valid(self, form):
        response = super().form_valid(form)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Equipement",
            object_id=self.object.pk,
            details={"code": self.object.code, "name": self.object.name},
        )
        messages.success(self.request, "Équipement ajouté avec succès.")
        return response


class EquipementUpdateView(RoleRequiredMixin, UpdateView):
    model = Equipement
    form_class = EquipementForm
    template_name = "equipment/equipment_form.html"
    success_url = reverse_lazy("equipment:list")
    allowed_roles = ["admin"]

    def form_valid(self, form):
        response = super().form_valid(form)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Equipement",
            object_id=self.object.pk,
            details={"code": self.object.code, "name": self.object.name},
        )
        messages.success(self.request, "Équipement mis à jour.")
        return response


class EquipementDeleteView(RoleRequiredMixin, DeleteView):
    model = Equipement
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("equipment:list")
    allowed_roles = ["admin"]

    def form_valid(self, form):
        request = self.request
        self.object = self.get_object()
        create_audit_log(
            user=request.user,
            action="delete",
            model_name="Equipement",
            object_id=self.object.pk,
            details={"code": self.object.code, "name": self.object.name},
        )
        messages.success(request, "Équipement supprimé.")
        return super().form_valid(form)


@login_required
def export_equipements_csv(request):
    if request.user.role != "admin":
        return HttpResponseForbidden("Export réservé à l'administrateur.")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="equipements.csv"'
    writer = csv.writer(response)
    writer.writerow(["Code", "Nom", "Type", "Fabricant", "Référence", "Localisation", "Statut", "Criticité"])
    for eq in Equipement.objects.all():
        writer.writerow(
            [
                eq.code,
                eq.name,
                eq.equipment_type,
                eq.manufacturer,
                eq.reference,
                eq.location,
                eq.status,
                eq.criticality,
            ]
        )
    return response
