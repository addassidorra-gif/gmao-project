# Generated manually on 2026-05-06 to accept legacy criticality values

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0004_clean_locations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipement',
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
                verbose_name='Criticité',
            ),
        ),
    ]
