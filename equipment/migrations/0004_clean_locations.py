# Generated manually on 2026-05-04 for cleaning up location data duplicates

from django.db import migrations


def clean_locations(apps, schema_editor):
    """Standardize location names to remove duplicates and inconsistencies"""
    Equipement = apps.get_model('equipment', 'Equipement')
    
    # Consolidate location variations
    Equipement.objects.filter(location='Labo industriel').update(location='Labo Industriel (GI)')
    Equipement.objects.filter(location='Labo mécanique').update(location='Labo Mécanique')
    Equipement.objects.filter(location='Labo matériaux (GM)').update(location='Labo Matériaux (GM)')
    Equipement.objects.filter(location='Atelier Robot').update(location='Labo Automatisme')
    Equipement.objects.filter(location='Labo Info').update(location='Labo Informatique')
    Equipement.objects.filter(location='Labo industriel (GI)').update(location='Labo Industriel (GI)')


def reverse_locations(apps, schema_editor):
    """Reverse location standardization (not comprehensive, but basic reverse)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0003_data_migration_update_criticality'),
    ]

    operations = [
        migrations.RunPython(clean_locations, reverse_locations),
    ]
