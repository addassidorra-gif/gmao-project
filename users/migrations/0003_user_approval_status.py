from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="approval_status",
            field=models.CharField(
                choices=[
                    ("pending", "En attente"),
                    ("accepted", "Accepté"),
                    ("rejected", "Refusé"),
                ],
                default="accepted",
                max_length=20,
            ),
        ),
    ]
