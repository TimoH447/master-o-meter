# Generated by Django 4.2.15 on 2025-01-06 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0017_remove_event_blocking_events_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='conditions',
            field=models.ManyToManyField(blank=True, related_name='events_of_condition', to='pomo.eventcondition'),
        ),
    ]
