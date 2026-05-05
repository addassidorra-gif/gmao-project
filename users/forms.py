from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class StyledFormMixin:
    def apply_style(self):
        for field in self.fields.values():
            css_class = "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class LoginForm(AuthenticationForm, StyledFormMixin):
    username = forms.EmailField(label="Adresse email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "admin@enib.tn"
        self.fields["password"].widget.attrs["placeholder"] = "Mot de passe"
        self.apply_style()


class UserForm(forms.ModelForm, StyledFormMixin):
    password = forms.CharField(
        label="Mot de passe",
        required=False,
        widget=forms.PasswordInput,
        help_text="Laisser vide pour conserver le mot de passe actuel.",
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "role", "approval_status", "is_active", "password"]
        labels = {
            "full_name": "Nom complet",
            "email": "Adresse email",
            "role": "Rôle",
            "approval_status": "Validation administrateur",
            "is_active": "Compte actif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style()

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if user.approval_status == User.ApprovalStatus.ACCEPTED:
            user.is_active = True
        elif user.approval_status in [User.ApprovalStatus.PENDING, User.ApprovalStatus.REJECTED]:
            user.is_active = False
        if commit:
            user.save()
        return user
