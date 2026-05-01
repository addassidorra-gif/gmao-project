from django import forms

from .models import Equipement


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = [
            "code",
            "name",
            "equipment_type",
            "manufacturer",
            "reference",
            "location",
            "status",
            "criticality",
            "purchase_date",
            "description",
        ]
        labels = {
            "equipment_type": "Type",
            "purchase_date": "Date d'achat",
            "description": "Description",
        }
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
