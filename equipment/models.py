from django.db import models


class Equipement(models.Model):
    class Status(models.TextChoices):
        EN_SERVICE = "En service", "En service"
        EN_PANNE = "En panne", "En panne"
        EN_MAINTENANCE = "En maintenance", "En maintenance"
        HORS_SERVICE = "Hors service", "Hors service"

    class Criticality(models.TextChoices):
        TRES_ELEVEE = "Très élevée", "Très élevée"
        ELEVEE = "Élevée", "Élevée"
        MOYENNE = "Moyenne", "Moyenne"
        FAIBLE = "Faible", "Faible"

    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    name = models.CharField(max_length=255, verbose_name="Nom")
    equipment_type = models.CharField(max_length=255, verbose_name="Type")
    manufacturer = models.CharField(max_length=255, blank=True, verbose_name="Fabricant")
    reference = models.CharField(max_length=255, blank=True, verbose_name="Référence")
    location = models.CharField(max_length=255, verbose_name="Localisation")
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.EN_SERVICE, verbose_name="Statut")
    criticality = models.CharField(
        max_length=50,
        choices=Criticality.choices,
        default=Criticality.MOYENNE,
        verbose_name="Criticité",
    )
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Date d'achat")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "code"]
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        indexes = [
            models.Index(fields=["status"], name="equipment_status_idx"),
            models.Index(fields=["location"], name="equipment_location_idx"),
            models.Index(fields=["criticality"], name="equipment_criticality_idx"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
