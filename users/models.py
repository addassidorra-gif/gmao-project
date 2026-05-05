from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RESPONSABLE = "responsable", "Resp. Atelier"
        TECHNICIEN = "technicien", "Technicien"
        OPERATEUR = "operateur", "Opérateur"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "En attente"
        ACCEPTED = "accepted", "Accepté"
        REJECTED = "rejected", "Refusé"

    ROLE_HIERARCHY = {
        Role.OPERATEUR: 10,
        Role.TECHNICIEN: 20,
        Role.RESPONSABLE: 30,
        Role.ADMIN: 40,
    }

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERATEUR)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.ACCEPTED,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        ordering = ["full_name", "email"]
        indexes = [
            models.Index(fields=["role"], name="user_role_idx"),
            models.Index(fields=["approval_status"], name="user_approval_idx"),
            models.Index(fields=["is_active"], name="user_active_idx"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def initials(self):
        parts = [part for part in self.full_name.split() if part]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0][:2].upper()
        return f"{parts[0][0]}{parts[1][0]}".upper()

    @property
    def status_label(self):
        if self.approval_status == self.ApprovalStatus.PENDING:
            return "En attente"
        if self.approval_status == self.ApprovalStatus.REJECTED:
            return "Refusé"
        return "Actif" if self.is_active else "Inactif"

    @property
    def approval_status_label(self):
        return self.get_approval_status_display()

    @property
    def display_id(self):
        return f"U{self.pk:03d}" if self.pk else "U000"

    @property
    def role_label(self):
        return self.get_role_display()

    def has_role_at_least(self, role: str) -> bool:
        current_rank = self.ROLE_HIERARCHY.get(self.role, 0)
        required_rank = self.ROLE_HIERARCHY.get(role, 0)
        return current_rank >= required_rank

    @property
    def is_workshop_manager(self):
        return self.role == self.Role.RESPONSABLE
