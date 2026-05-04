# Generated manually on 2026-05-04 for data migration from old to new priority values

from django.db import migrations


def update_priority_values(apps, schema_editor):
    """Convert old priority values to new ones"""
    Incident = apps.get_model('maintenance', 'Incident')
    Intervention = apps.get_model('maintenance', 'Intervention')
    
    # Update Incident priorities
    Incident.objects.filter(priority='Urgente').update(priority='Très urgent')
    Incident.objects.filter(priority='Normale').update(priority='Normal')
    Incident.objects.filter(priority='Faible').update(priority='Normal')
    
    # Update Intervention priorities
    Intervention.objects.filter(priority='Urgente').update(priority='Très urgent')
    Intervention.objects.filter(priority='Normale').update(priority='Normal')
    Intervention.objects.filter(priority='Faible').update(priority='Normal')


def update_criticality_values(apps, schema_editor):
    """Convert Haute criticality to Élevée"""
    Incident = apps.get_model('maintenance', 'Incident')
    
    # Update criticality
    Incident.objects.filter(criticality='Haute').update(criticality='Élevée')


def reverse_priority_values(apps, schema_editor):
    """Reverse the priority value updates"""
    Incident = apps.get_model('maintenance', 'Incident')
    Intervention = apps.get_model('maintenance', 'Intervention')
    
    Incident.objects.filter(priority='Très urgent').update(priority='Urgente')
    Incident.objects.filter(priority='Normal').update(priority='Normale')
    
    Intervention.objects.filter(priority='Très urgent').update(priority='Urgente')
    Intervention.objects.filter(priority='Normal').update(priority='Normale')


def reverse_criticality_values(apps, schema_editor):
    """Reverse the criticality value updates"""
    Incident = apps.get_model('maintenance', 'Incident')
    
    Incident.objects.filter(criticality='Élevée').update(criticality='Haute')


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0003_alter_maintenance_priorities'),
    ]

    operations = [
        migrations.RunPython(update_priority_values, reverse_priority_values),
        migrations.RunPython(update_criticality_values, reverse_criticality_values),
    ]
