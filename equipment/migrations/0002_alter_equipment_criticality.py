# Generated manually on 2026-05-04 to update equipment criticality choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),
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
                ],
                default='Moyenne',
                max_length=50,
                verbose_name='Criticité',
            ),
        ),
    ]
