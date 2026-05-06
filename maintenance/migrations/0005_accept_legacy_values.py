# Generated manually on 2026-05-06 to accept legacy values in choice fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0004_data_migration_update_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='priority',
            field=models.CharField(
                choices=[
                    ('Très urgent', 'Très urgent'),
                    ('Urgent', 'Urgent'),
                    ('Normal', 'Normal'),
                    # Legacy values for backward compatibility
                    ('Urgente', 'Urgente'),
                    ('Normale', 'Normale'),
                    ('Faible', 'Faible'),
                    ('Pas urgente', 'Pas urgente'),
                ],
                default='Normal',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='incident',
            name='criticality',
            field=models.CharField(
                choices=[
                    ('Très élevée', 'Très élevée'),
                    ('Élevée', 'Élevée'),
                    ('Moyenne', 'Moyenne'),
                    ('Faible', 'Faible'),
                    # Legacy value for backward compatibility
                    ('Haute', 'Haute'),
                ],
                default='Moyenne',
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='priority',
            field=models.CharField(
                choices=[
                    ('Très urgent', 'Très urgent'),
                    ('Urgent', 'Urgent'),
                    ('Normal', 'Normal'),
                    # Legacy values for backward compatibility
                    ('Urgente', 'Urgente'),
                    ('Normale', 'Normale'),
                    ('Faible', 'Faible'),
                    ('Pas urgente', 'Pas urgente'),
                ],
                default='Normal',
                max_length=20,
            ),
        ),
    ]
