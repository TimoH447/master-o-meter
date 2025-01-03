# Generated by Django 4.2.15 on 2024-08-19 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesis_tracker', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailyprogress',
            old_name='page_count',
            new_name='cites',
        ),
        migrations.RenameField(
            model_name='dailyprogress',
            old_name='word_count',
            new_name='equations',
        ),
        migrations.AddField(
            model_name='dailyprogress',
            name='figures',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyprogress',
            name='inlines',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyprogress',
            name='pages',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyprogress',
            name='words',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
