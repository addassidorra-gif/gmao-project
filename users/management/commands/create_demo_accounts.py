from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEMO_ACCOUNTS = [
    {
        "email": "admin@enib.tn",
        "full_name": "Ahmed Ben Ali",
        "password": "admin123",
        "role": User.Role.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "responsable@enib.tn",
        "full_name": "Mohamed Trabelski",
        "password": "resp123",
        "role": User.Role.RESPONSABLE,
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "operateur@enib.tn",
        "full_name": "Lina Mansour",
        "password": "oper123",
        "role": User.Role.OPERATEUR,
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "technicien@enib.tn",
        "full_name": "Hbib Hamemi",
        "password": "tech123",
        "role": User.Role.TECHNICIEN,
        "is_staff": False,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = "Crée les comptes de démonstration pour accès rapide"

    def handle(self, *args, **options):
        for account in DEMO_ACCOUNTS:
            user, created = User.objects.get_or_create(
                email=account["email"],
                defaults={
                    "full_name": account["full_name"],
                    "role": account["role"],
                    "is_active": True,
                    "is_staff": account["is_staff"],
                    "is_superuser": account["is_superuser"],
                    "approval_status": User.ApprovalStatus.ACCEPTED,
                },
            )

            # Toujours mettre à jour le mot de passe et les champs essentiels
            user.set_password(account["password"])
            user.full_name = account["full_name"]
            user.role = account["role"]
            user.is_active = True
            user.is_staff = account["is_staff"]
            user.is_superuser = account["is_superuser"]
            user.approval_status = User.ApprovalStatus.ACCEPTED
            user.save()

            status = "créé" if created else "mis à jour"
            self.stdout.write(
                self.style.SUCCESS(f"✓ Compte {account['email']} {status} avec succès")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ {len(DEMO_ACCOUNTS)} comptes de démonstration sont prêts !"
            )
        )
        self.stdout.write(self.style.WARNING("\nComptes disponibles:"))
        for account in DEMO_ACCOUNTS:
            self.stdout.write(f"  • {account['email']} / {account['password']}")
