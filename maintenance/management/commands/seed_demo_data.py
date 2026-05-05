from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from equipment.models import Equipement
from maintenance.models import AuditLog, Incident, Intervention


USER_DATA = [
    {"email": "admin@enib.tn", "full_name": "Ahmed Ben Ali", "role": "admin", "password": "admin123", "is_staff": True},
    {"email": "responsable@enib.tn", "full_name": "Mohamed Trabelsi", "role": "responsable", "password": "resp123"},
    {"email": "operateur@enib.tn", "full_name": "Lina Mansour", "role": "operateur", "password": "oper123"},
    {"email": "sara@enib.tn", "full_name": "Sara Kouki", "role": "operateur", "password": "oper123"},
    {"email": "technicien@enib.tn", "full_name": "Hbib Hamemi", "role": "technicien", "password": "tech123"},
    {"email": "riadh@enib.tn", "full_name": "Riadh Garbi", "role": "technicien", "password": "tech123"},
    {"email": "karim@enib.tn", "full_name": "Karim Salah", "role": "technicien", "password": "tech123"},
]

EQUIPMENT_DATA = [
    {"code": "68/19", "name": "Machine de traction TESTCOM 10", "equipment_type": "Machine d'essai mécanique", "manufacturer": "TESTCOM", "reference": "68/19", "location": "Laboratoire Matériaux", "status": "En service", "criticality": "Très élevée", "year": 2019},
    {"code": "311/11", "name": "Banc régulation niveau et débit", "equipment_type": "Banc didactique automatisme", "manufacturer": "", "reference": "311/11", "location": "Laboratoire Génie Industriel", "status": "En service", "criticality": "Élevée", "year": 2011},
    {"code": "314/11", "name": "Système didactique de régulation", "equipment_type": "Banc thermique / automatique", "manufacturer": "", "reference": "314/11", "location": "Laboratoire Génie Industriel", "status": "En maintenance", "criticality": "Moyenne", "year": 2013},
    {"code": "62/18", "name": "Banc Jominy", "equipment_type": "Machine d'essai thermique", "manufacturer": "", "reference": "62/18", "location": "Laboratoire Génie Mécanique", "status": "En panne", "criticality": "Élevée", "year": 2018},
    {"code": "FC015", "name": "Automate programmable (API)", "equipment_type": "Électronique", "manufacturer": "Siemens", "reference": "100/04/02/07", "location": "Laboratoire Automatisme", "status": "En panne", "criticality": "Élevée", "year": 2020},
    {"code": "VC022", "name": "Robot industriel", "equipment_type": "Robot", "manufacturer": "KUKA", "reference": "100/05/05/06", "location": "Laboratoire Automatisme", "status": "En maintenance", "criticality": "Élevée", "year": 2021},
    {"code": "FC017", "name": "PC Dell", "equipment_type": "Informatique", "manufacturer": "Dell", "reference": "300/07/03/11", "location": "Laboratoire Informatique", "status": "En service", "criticality": "Faible", "year": 2020},
    {"code": "FC011", "name": "Tour CNC", "equipment_type": "Machine-outil", "manufacturer": "DMG MORI", "reference": "100/03/05/08", "location": "Laboratoire Génie Mécanique", "status": "Hors service", "criticality": "Élevée", "year": 2018},
    {"code": "VC031", "name": "Compresseur d'air", "equipment_type": "Machine", "manufacturer": "Atlas Copco", "reference": "300/02/04/01", "location": "Laboratoire Génie Mécanique", "status": "En service", "criticality": "Moyenne", "year": 2017},
]

INCIDENT_DATA = [
    {"code": "P001", "equipment": "FC015", "technician": "technicien@enib.tn", "operator": "operateur@enib.tn", "title": "API ne démarre pas", "description": "Absence de démarrage du processeur.", "criticality": "Moyenne", "priority": "Normal", "status": "En attente", "date": "2024-05-27"},
    {"code": "P002", "equipment": "VC031", "technician": "technicien@enib.tn", "operator": "sara@enib.tn", "title": "Fuite hydraulique", "description": "Fuite hydraulique au niveau du joint d'étanchéité.", "criticality": "Élevée", "priority": "Très urgent", "status": "Résolue", "date": "2026-01-07"},
    {"code": "P003", "equipment": "VC022", "technician": "karim@enib.tn", "operator": "operateur@enib.tn", "title": "Erreur capteur", "description": "Signal incohérent sur l'axe 3.", "criticality": "Moyenne", "priority": "Normal", "status": "En attente", "date": "2025-12-12"},
]

INTERVENTION_DATA = [
    {"code": "I001", "incident": "P001", "technician": "technicien@enib.tn", "equipment": "FC015", "description": "Remplacement carte mère processeur", "type": "Corrective", "priority": "Très urgent", "status": "Terminée", "report": "Carte CPU remplacée avec succès.", "start_date": "2024-05-27", "end_date": "2024-10-15", "next_maintenance": "2025-05-27", "equipment_status_after": "En service"},
    {"code": "I002", "incident": "P002", "technician": "karim@enib.tn", "equipment": "VC031", "description": "Réparation fuite joint d'étanchéité", "type": "Corrective", "priority": "Très urgent", "status": "Terminée", "report": "Joint remplacé, test de pression validé.", "start_date": "2026-04-07", "end_date": "2026-04-24", "next_maintenance": "2026-10-07", "equipment_status_after": "En service"},
    {"code": "I003", "incident": "P003", "technician": "karim@enib.tn", "equipment": "VC022", "description": "Diagnostic capteurs de position", "type": "Corrective", "priority": "Normal", "status": "En cours", "report": "", "start_date": "2026-04-24", "end_date": "", "next_maintenance": "", "equipment_status_after": "En maintenance"},
]


class Command(BaseCommand):
    help = "Charge des données de démonstration pour la GMAO."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Autorise explicitement le seed sur PostgreSQL/Supabase ou en DEBUG=False.",
        )

    def handle(self, *args, **options):
        if (connection.vendor == "postgresql" or not settings.DEBUG) and not options["allow_production"]:
            self.stdout.write(
                self.style.ERROR(
                    "Seed annulé: base PostgreSQL/production détectée. "
                    "Utilisez --allow-production seulement si vous voulez vraiment écrire les données de démonstration."
                )
            )
            return

        User = get_user_model()
        users_by_email = {}

        for item in USER_DATA:
            user, created = User.objects.get_or_create(
                email=item["email"],
                defaults={
                    "full_name": item["full_name"],
                    "role": item["role"],
                    "is_staff": item.get("is_staff", item["role"] == "admin"),
                    "is_superuser": item["role"] == "admin",
                    "is_active": item.get("is_active", True),
                    "approval_status": User.ApprovalStatus.ACCEPTED if item.get("is_active", True) else User.ApprovalStatus.REJECTED,
                },
            )
            user.full_name = item["full_name"]
            user.role = item["role"]
            user.is_staff = item.get("is_staff", item["role"] == "admin")
            user.is_superuser = item["role"] == "admin"
            user.is_active = item.get("is_active", True)
            user.approval_status = User.ApprovalStatus.ACCEPTED if user.is_active else User.ApprovalStatus.REJECTED
            user.set_password(item["password"])
            user.save()
            users_by_email[user.email] = user
            label = "créé" if created else "mis à jour"
            self.stdout.write(self.style.SUCCESS(f"Utilisateur {user.email} {label}"))

        equipment_by_code = {}
        for item in EQUIPMENT_DATA:
            equipment, _ = Equipement.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "equipment_type": item["equipment_type"],
                    "manufacturer": item["manufacturer"],
                    "reference": item["reference"],
                    "location": item["location"],
                    "status": item["status"],
                    "criticality": item["criticality"],
                    "purchase_date": date(item["year"], 1, 1),
                },
            )
            equipment_by_code[equipment.code] = equipment

        incident_by_code = {}
        for item in INCIDENT_DATA:
            incident, _ = Incident.objects.update_or_create(
                code=item["code"],
                defaults={
                    "equipment": equipment_by_code[item["equipment"]],
                    "technician": users_by_email[item["technician"]],
                    "operator": users_by_email[item["operator"]],
                    "title": item["title"],
                    "description": item["description"],
                    "criticality": item["criticality"],
                    "priority": item["priority"],
                    "status": item["status"],
                    "reported_at": timezone.make_aware(datetime.fromisoformat(item["date"])),
                },
            )
            incident_by_code[incident.code] = incident

        for item in INTERVENTION_DATA:
            Intervention.objects.update_or_create(
                code=item["code"],
                defaults={
                    "incident": incident_by_code.get(item["incident"]) if item["incident"] else None,
                    "equipment": equipment_by_code[item["equipment"]],
                    "technician": users_by_email[item["technician"]],
                    "description": item["description"],
                    "intervention_type": item["type"],
                    "priority": item["priority"],
                    "status": item["status"],
                    "report": item["report"],
                    "start_date": date.fromisoformat(item["start_date"]),
                    "end_date": date.fromisoformat(item["end_date"]) if item["end_date"] else None,
                    "next_maintenance": date.fromisoformat(item["next_maintenance"]) if item["next_maintenance"] else None,
                    "equipment_status_after": item["equipment_status_after"],
                },
            )

        AuditLog.objects.get_or_create(
            action="seed",
            model_name="System",
            object_id="demo-data",
            defaults={"details": {"message": "Données de démonstration chargées."}},
        )

        self.stdout.write(self.style.SUCCESS("Jeu de données de démonstration chargé avec succès."))
