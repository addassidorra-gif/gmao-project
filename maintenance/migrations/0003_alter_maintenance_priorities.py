# Generated manually on 2026-05-04 to update maintenance field choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0002_initial'),
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
                ],
                default='Normal',
                max_length=20,
            ),
        ),
    ]
