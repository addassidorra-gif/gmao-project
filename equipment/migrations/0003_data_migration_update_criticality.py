# Generated manually on 2026-05-04 for equipment criticality data migration

from django.db import migrations


def update_equipment_criticality(apps, schema_editor):
    """Convert Haute criticality to Élevée for equipment"""
    Equipement = apps.get_model('equipment', 'Equipement')
    
    # Update criticality
    Equipement.objects.filter(criticality='Haute').update(criticality='Élevée')


def reverse_equipment_criticality(apps, schema_editor):
    """Reverse the equipment criticality updates"""
    Equipement = apps.get_model('equipment', 'Equipement')
    
    Equipement.objects.filter(criticality='Élevée').update(criticality='Haute')


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0002_alter_equipment_criticality'),
    ]

    operations = [
        migrations.RunPython(update_equipment_criticality, reverse_equipment_criticality),
    ]
