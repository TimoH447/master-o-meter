from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
#from django.contrib.postgres.fields import ArrayField
from datetime import timedelta
from django.utils import timezone

class Timers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(default=1)  # 1 for 25 min, 2 for 50 min
    date_completed = models.DateField(default=timezone.now)  # Date when the timer was completed
    time_completed = models.TimeField(auto_now_add=True, null=True,blank=True)  # Time when the timer was completed

    def __str__(self):
        return f"{self.user.username} - {self.duration} pomodoro(s) on {self.date_completed}"

class Location(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name

"""
class LocationState(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    retrieved_scroll = models.BooleanField(default=False)  # Unlocks story progression in the library
"""    


class Event(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField()  # Story text
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # Location name
    
    #Event is completed direct or after a timer
    completion_type = models.CharField(max_length=50, blank=True, null=True, choices=[('direct','direct'),('25','25')], default='direct')
    
    # Conditions
    related_events_completed = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False, 
        related_name='dependent_events'
    )  # Events that must be completed before this one triggers

    blocking_events = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False, 
        related_name='blocked_events'
    )  # Events that, if completed, block this event
    
    # Outcomes
    unlock_event_id = models.IntegerField(null=True, blank=True)  # ID of an event to unlock
    
    # Meta

    def __str__(self):
        return f"Event: {self.name} at {self.location.name}"

        # Add any logic to determine if this event can be triggered
    def can_be_triggered(self, player_state):
        """
        Checks if the event can be triggered based on the player's current state.
        :param player_state: PlayerState instance
        :return: Boolean indicating if the event can be triggered
        """
        # Check if the event has been completed by the player
        #if self in player_state.completed_events.all():
        #    return False
        
        # Check if the related events have been completed by the player
        if self.related_events_completed.exists():
            for required_event in self.related_events_completed.all():
                if required_event not in player_state.completed_events.all():
                    return False  # Condition not met
        
        # Check if any of the blocking events have been completed by the player
        if self.blocking_events.exists():
            for blocking_event in self.blocking_events.all():
                if blocking_event in player_state.completed_events.all():
                    return False  # Blocked by a completed event


        return True  # All conditions met

class PlayerState(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Many-to-many field for tracking which events the player has completed
    completed_events = models.ManyToManyField(Event, blank=True, null=True)  # Events the player has completed

    def __str__(self):
        return self.player.username

    def get_streak(self):
        # Get all Pomodoros completed by the user, ordered by date
        pomodoros = Timers.objects.filter(user=self.player).order_by('-date_completed')

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
    
    def get_total_pomos_today(self):
        # Get the current date
        today = timezone.now().date()
        # Get all Pomodoros completed by the user today
        timers_today = Timers.objects.filter(user=self.player, date_completed=today)
        # Count how many Pomodoros have been completed today
        total_pomodoros_today = timers_today.aggregate(total=models.Sum('duration'))['total'] or 0
        return total_pomodoros_today

    def get_total_pomos(self): 
        # Get all Pomodoros completed by the user (no date filter for all-time total)
        timers_alltime = Timers.objects.filter(user=self.player)
        # Sum the total number of Pomodoros completed all-time
        total_pomodoros_alltime = timers_alltime.aggregate(total=models.Sum('duration'))['total'] or 0
        return total_pomodoros_alltime

class Currency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user}'s Points"
