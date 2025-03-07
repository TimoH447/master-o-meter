# Generated by Django 4.2.15 on 2024-12-28 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0010_reward_claimed'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='info_box_btn_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='post_timer_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='pre_timer_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='repeatable',
            field=models.BooleanField(default=False),
        ),
    ]
