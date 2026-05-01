from django.conf import settings
from django.db import models
from django.utils import timezone

from equipment.models import Equipement


def generate_code(model_class, prefix: str) -> str:
    last_code = (
        model_class.objects.filter(code__startswith=prefix)
        .order_by("-code")
        .values_list("code", flat=True)
        .first()
    )
    if not last_code:
        return f"{prefix}001"

    try:
        number = int(last_code.replace(prefix, "", 1))
    except ValueError:
        number = model_class.objects.count()
    return f"{prefix}{number + 1:03d}"


class Incident(models.Model):
    class Priority(models.TextChoices):
        URGENTE = "Urgente", "Urgente"
        NORMALE = "Normale", "Normale"
        FAIBLE = "Faible", "Faible"

    class Status(models.TextChoices):
        EN_ATTENTE = "En attente", "En attente"
        EN_COURS = "En cours", "En cours"
        RESOLUE = "Résolue", "Résolue"

    code = models.CharField(max_length=20, unique=True, blank=True)
    equipment = models.ForeignKey(Equipement, on_delete=models.PROTECT, related_name="incidents")
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_incidents",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    criticality = models.CharField(
        max_length=50,
        choices=Equipement.Criticality.choices,
        default=Equipement.Criticality.MOYENNE,
    )
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMALE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EN_ATTENTE)
    reported_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reported_at", "-id"]
        verbose_name = "Panne"
        verbose_name_plural = "Pannes"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code(Incident, "P")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Intervention(models.Model):
    class Type(models.TextChoices):
        CORRECTIVE = "Corrective", "Corrective"
        PREVENTIVE = "Préventive", "Préventive"

    class Status(models.TextChoices):
        PLANIFIEE = "Planifiée", "Planifiée"
        EN_COURS = "En cours", "En cours"
        TERMINEE = "Terminée", "Terminée"

    code = models.CharField(max_length=20, unique=True, blank=True)
    incident = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interventions",
    )
    equipment = models.ForeignKey(Equipement, on_delete=models.PROTECT, related_name="interventions")
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interventions",
    )
    intervention_type = models.CharField(max_length=20, choices=Type.choices, default=Type.CORRECTIVE)
    priority = models.CharField(max_length=20, choices=Incident.Priority.choices, default=Incident.Priority.NORMALE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EN_COURS)
    description = models.TextField()
    report = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    equipment_status_after = models.CharField(max_length=50, choices=Equipement.Status.choices, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code(Intervention, "I")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.equipment.name}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"

    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.object_id}"
