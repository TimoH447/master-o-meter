# Generated by Django 4.2.15 on 2024-10-06 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0003_event_location_playerstate_event_location_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='intelligence_increase',
        ),
        migrations.RemoveField(
            model_name='event',
            name='is_replayable',
        ),
    ]
