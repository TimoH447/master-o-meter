from datetime import timedelta
from django.utils import timezone
from .models import Timers

def calculate_streak(user):
    # Get all Pomodoros completed by the user, ordered by date
    pomodoros = Timers.objects.filter(user=user).order_by('-date_completed')

    if not pomodoros.exists():
        return 0  # No pomodoros, so no streak

    # Initialize streak and today's date
    streak = 0
    today = timezone.now().date()
    yesterday = today - timedelta(1)

    # Check if the user completed a Pomodoro today
    if pomodoros[0].date_completed == today or pomodoros[0].date_completed == yesterday:
        streak = 1  # User completed a Pomodoro today, start streak count
        # Iterate through the user's Pomodoros to calculate the streak
        for i in range(1, len(pomodoros)):
            prev_day = pomodoros[i - 1].date_completed
            current_day = pomodoros[i].date_completed
            
            # If the current day is exactly one day before the previous day, continue the streak
            if prev_day - current_day == timedelta(days=1):
                streak += 1
            # If the days are not consecutive, break the streak
            elif prev_day - current_day > timedelta(days=1):
                break

    return streak
