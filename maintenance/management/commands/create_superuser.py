from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if it does not exist"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@gmao.local",
                password="admin123456",
                role="admin"
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created superuser "admin" with password "admin123456"'
                )
            )
        else:
            self.stdout.write("Superuser 'admin' already exists")
