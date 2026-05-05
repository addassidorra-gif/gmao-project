import time
import uuid

from django.core.management.base import BaseCommand
from django.db import connection

from equipment.models import Equipement
from maintenance.models import AuditLog, Incident, Intervention
from users.models import User


class Command(BaseCommand):
    help = "Audit the active Django database connection and optionally run a safe CRUD write test."

    def add_arguments(self, parser):
        parser.add_argument(
            "--write-test",
            action="store_true",
            help="Create, update, read, and delete a temporary equipment row, then commit the deletion.",
        )

    def handle(self, *args, **options):
        db = connection.settings_dict
        host = db.get("HOST") or "local file"
        engine = db.get("ENGINE", "")
        database = db.get("NAME") or ""

        self.stdout.write(self.style.MIGRATE_HEADING("Database connection audit"))
        self.stdout.write(f"Engine: {engine}")
        self.stdout.write(f"Vendor: {connection.vendor}")
        self.stdout.write(f"Host: {host}")
        self.stdout.write(f"Database: {database}")

        if connection.vendor != "postgresql":
            self.stdout.write(
                self.style.WARNING(
                    "This project is not currently using PostgreSQL. "
                    "If you expect Supabase, check DATABASE_URL."
                )
            )
        elif "supabase" in str(host).lower():
            self.stdout.write(self.style.SUCCESS("Supabase-like PostgreSQL host detected."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "PostgreSQL is active, but the host does not look like Supabase. "
                    "This can be normal if you use a pooler/custom host."
                )
            )

        start = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            result = cursor.fetchone()
        elapsed_ms = (time.perf_counter() - start) * 1000

        if result != (1,):
            raise RuntimeError("Unexpected database response to SELECT 1.")

        self.stdout.write(self.style.SUCCESS(f"Read probe OK ({elapsed_ms:.1f} ms)."))
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Current row counts"))

        models = [
            ("users.User", User),
            ("equipment.Equipement", Equipement),
            ("maintenance.Incident", Incident),
            ("maintenance.Intervention", Intervention),
            ("maintenance.AuditLog", AuditLog),
        ]
        for label, model in models:
            model_start = time.perf_counter()
            count = model.objects.count()
            model_elapsed = (time.perf_counter() - model_start) * 1000
            self.stdout.write(f"{label}: {count} rows ({model_elapsed:.1f} ms)")

        if options["write_test"]:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("CRUD write test"))
            code = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"

            write_start = time.perf_counter()
            equipement = Equipement.objects.create(
                code=code,
                name="Audit Supabase temporaire",
                equipment_type="Test",
                location="Audit",
                criticality="Faible",
                status="En service",
            )
            self.stdout.write(self.style.SUCCESS(f"Create OK: {code}"))

            equipement.status = "En maintenance"
            equipement.save(update_fields=["status"])
            refreshed = Equipement.objects.get(pk=equipement.pk)
            if refreshed.status != "En maintenance":
                raise RuntimeError("Update verification failed.")
            self.stdout.write(self.style.SUCCESS("Update + read-back OK"))

            pk = equipement.pk
            equipement.delete()
            if Equipement.objects.filter(pk=pk).exists():
                raise RuntimeError("Delete verification failed.")
            write_elapsed = (time.perf_counter() - write_start) * 1000
            self.stdout.write(self.style.SUCCESS(f"Delete OK ({write_elapsed:.1f} ms)."))
            self.stdout.write(
                self.style.SUCCESS("CRUD write test completed. No temporary row remains.")
            )
