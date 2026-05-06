from django.core.management.base import BaseCommand
from django.db import connection

from equipment.models import Equipement
from maintenance.models import Incident, Intervention


class Command(BaseCommand):
    help = "Nettoie et normalise les anciennes valeurs de priorité et criticité"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Nettoyage des anciennes valeurs en base de données..."))

        # Mapping des anciennes valeurs vers les nouvelles
        legacy_priority_map = {
            "Urgente": "Très urgent",
            "Normale": "Normal",
            "Faible": "Normal",
            "Pas urgente": "Normal",
        }

        legacy_criticality_map = {
            "Haute": "Élevée",
        }

        # Nettoyage des priorités dans Incident
        for old_value, new_value in legacy_priority_map.items():
            count = Incident.objects.filter(priority=old_value).update(priority=new_value)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  OK Incident: {count} priorite(s) '{old_value}' convertie(s) en '{new_value}'"))

        # Nettoyage des priorités dans Intervention
        for old_value, new_value in legacy_priority_map.items():
            count = Intervention.objects.filter(priority=old_value).update(priority=new_value)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  OK Intervention: {count} priorite(s) '{old_value}' convertie(s) en '{new_value}'"))

        # Nettoyage des criticités dans Incident
        for old_value, new_value in legacy_criticality_map.items():
            count = Incident.objects.filter(criticality=old_value).update(criticality=new_value)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  OK Incident: {count} criticite(s) '{old_value}' convertie(s) en '{new_value}'"))

        # Nettoyage des criticités dans Equipement
        for old_value, new_value in legacy_criticality_map.items():
            count = Equipement.objects.filter(criticality=old_value).update(criticality=new_value)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  OK Equipement: {count} criticite(s) '{old_value}' convertie(s) en '{new_value}'"))

        self.stdout.write(self.style.SUCCESS("\nOK Nettoyage des donnees termine avec succes."))
