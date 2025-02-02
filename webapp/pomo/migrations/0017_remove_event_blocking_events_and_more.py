# Generated by Django 4.2.15 on 2025-01-06 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0016_remove_friendrequest_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='blocking_events',
        ),
        migrations.RemoveField(
            model_name='event',
            name='related_events_completed',
        ),
        migrations.RemoveField(
            model_name='event',
            name='unlock_event_id',
        ),
        migrations.CreateModel(
            name='EventCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('condition_type', models.CharField(choices=[('all_completed', 'All of the specified events must be completed'), ('any_completed', 'Any of the specified events must be completed'), ('none_completed', 'None of the specified events must be completed'), ('time_based', 'Triggered within a specific time span'), ('state_based', 'Triggered based on player state')], max_length=50)),
                ('required_count', models.IntegerField(default=1)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('required_state', models.CharField(blank=True, max_length=255, null=True)),
                ('events', models.ManyToManyField(blank=True, related_name='condition_events', to='pomo.event')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='conditions',
            field=models.ManyToManyField(blank=True, related_name='events_with_conditions', to='pomo.eventcondition'),
        ),
    ]
