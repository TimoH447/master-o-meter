from django.db import migrations

def convert_duration_to_seconds(apps, schema_editor):
    Timers = apps.get_model('pomo', 'Timers')
    for timer in Timers.objects.all():
        if timer.duration == 1:
            timer.duration = 25 * 60  # Convert 1 unit to 1500 seconds (25 minutes)
        elif timer.duration == 2:
            timer.duration = 50 * 60  # Convert 2 units to 3000 seconds (50 minutes)
        timer.save()

class Migration(migrations.Migration):

    dependencies = [
        ('pomo', '0013_profile_friends_friendrequest'),  # Replace with the actual previous migration file
    ]

    operations = [
        migrations.RunPython(convert_duration_to_seconds),
    ]