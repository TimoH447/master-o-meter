# Generated by Django 4.2.15 on 2024-10-06 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0004_remove_event_intelligence_increase_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='completion_type',
            field=models.CharField(blank=True, choices=[('direct', 'direct'), ('25', '25')], default='direct', max_length=50, null=True),
        ),
    ]
