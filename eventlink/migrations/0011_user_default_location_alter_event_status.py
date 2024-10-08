# Generated by Django 5.0.8 on 2024-08-20 15:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eventlink", "0010_event_reason"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="default_location",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("accepted", "Accepted"),
                    ("rejected", "Rejected"),
                    ("canceled", "Canceled"),
                ],
                default="pending",
                max_length=10,
            ),
        ),
    ]
