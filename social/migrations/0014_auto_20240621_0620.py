# Generated by Django 3.2.25 on 2024-06-21 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_auto_20240621_0615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventmessagemodel',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_messages', to='social.event'),
        ),
        migrations.AlterField(
            model_name='messagemodel',
            name='thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='social.threadmodel'),
        ),
    ]