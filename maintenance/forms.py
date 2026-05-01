from django import forms

from users.models import User

from .models import Incident, Intervention


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "equipment",
            "operator",
            "technician",
            "title",
            "description",
            "criticality",
            "priority",
            "status",
        ]
        labels = {
            "equipment": "Équipement",
            "operator": "Opérateur",
            "technician": "Technicien",
            "title": "Titre",
            "description": "Description",
            "criticality": "Criticité",
            "priority": "Priorité",
            "status": "Statut",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].queryset = User.objects.filter(role=User.Role.TECHNICIEN, is_active=True)
        self.fields["operator"].queryset = User.objects.filter(role=User.Role.OPERATEUR, is_active=True)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()


class IncidentOperatorForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["equipment", "technician", "title", "description", "criticality", "priority"]
        labels = {
            "equipment": "Équipement",
            "technician": "Technicien",
            "title": "Titre",
            "description": "Description",
            "criticality": "Criticité",
            "priority": "Priorité",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].queryset = User.objects.filter(role=User.Role.TECHNICIEN, is_active=True)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            "incident",
            "equipment",
            "technician",
            "intervention_type",
            "priority",
            "status",
            "description",
            "report",
            "start_date",
            "end_date",
            "next_maintenance",
            "equipment_status_after",
        ]
        labels = {
            "incident": "Panne liée",
            "equipment": "Équipement",
            "technician": "Technicien",
            "intervention_type": "Type",
            "priority": "Priorité",
            "status": "Statut",
            "description": "Description",
            "report": "Rapport",
            "start_date": "Date de début",
            "end_date": "Date de fin",
            "next_maintenance": "Prochaine maintenance",
            "equipment_status_after": "Statut final de l'équipement",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "report": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "next_maintenance": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].queryset = User.objects.filter(role=User.Role.TECHNICIEN, is_active=True)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()

    def clean(self):
        cleaned_data = super().clean()
        incident = cleaned_data.get("incident")
        equipment = cleaned_data.get("equipment")
        if incident and equipment and incident.equipment_id != equipment.id:
            self.add_error("equipment", "L'équipement doit correspondre à la panne sélectionnée.")
        return cleaned_data


class TechnicianInterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ["status", "report", "end_date", "next_maintenance", "equipment_status_after"]
        labels = {
            "status": "Statut",
            "report": "Rapport",
            "end_date": "Date de fin",
            "next_maintenance": "Prochaine maintenance",
            "equipment_status_after": "Statut final de l'équipement",
        }
        widgets = {
            "report": forms.Textarea(attrs={"rows": 5}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "next_maintenance": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
