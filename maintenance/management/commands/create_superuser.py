import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if it does not exist"

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL") or os.getenv("ADMIN_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or os.getenv("ADMIN_PASSWORD")
        full_name = os.getenv("DJANGO_SUPERUSER_FULL_NAME", "Administrateur GMAO")

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Superuser skipped: set ADMIN_EMAIL and ADMIN_PASSWORD in the environment."
                )
            )
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name,
                role="admin",
                approval_status=User.ApprovalStatus.ACCEPTED,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{email}"'
                )
            )
        else:
            self.stdout.write(f'Superuser "{email}" already exists')
