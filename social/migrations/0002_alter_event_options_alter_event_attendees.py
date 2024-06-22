# Generated by Django 5.0.4 on 2024-06-15 12:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="event",
            options={"ordering": ["start_time"]},
        ),
        migrations.AlterField(
            model_name="event",
            name="attendees",
            field=models.ManyToManyField(
                blank=True, related_name="event_attendees", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
