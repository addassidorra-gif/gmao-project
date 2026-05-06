from django import forms

from users.models import User

from .models import Incident, Intervention


# Legacy value mappings for backward compatibility
LEGACY_PRIORITY_MAP = {
    "Urgente": "Très urgent",
    "Normale": "Normal",
    "Faible": "Normal",
    "Pas urgente": "Normal",
}

LEGACY_CRITICALITY_MAP = {
    "Haute": "Élevée",
}


def normalize_priority(value):
    """Convert legacy priority values to new ones"""
    if not value:
        return value
    return LEGACY_PRIORITY_MAP.get(value, value)


def normalize_criticality(value):
    """Convert legacy criticality values to new ones"""
    if not value:
        return value
    return LEGACY_CRITICALITY_MAP.get(value, value)


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

    def clean(self):
        cleaned_data = super().clean()
        # Normalize legacy values
        if "priority" in cleaned_data and cleaned_data["priority"]:
            cleaned_data["priority"] = normalize_priority(cleaned_data["priority"])
        if "criticality" in cleaned_data and cleaned_data["criticality"]:
            cleaned_data["criticality"] = normalize_criticality(cleaned_data["criticality"])
        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()
        # Normalize legacy values
        if "priority" in cleaned_data and cleaned_data["priority"]:
            cleaned_data["priority"] = normalize_priority(cleaned_data["priority"])
        if "criticality" in cleaned_data and cleaned_data["criticality"]:
            cleaned_data["criticality"] = normalize_criticality(cleaned_data["criticality"])
        return cleaned_data


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
        # Normalize legacy priority values
        if "priority" in cleaned_data and cleaned_data["priority"]:
            cleaned_data["priority"] = normalize_priority(cleaned_data["priority"])
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
