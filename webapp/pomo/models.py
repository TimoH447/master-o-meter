from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
#from django.contrib.postgres.fields import ArrayField
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_player_state(sender, instance, created, **kwargs):
    if created:
        PlayerState.objects.create(player=instance)
        Profile.objects.create(user=instance)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_developer = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='friend_set', blank=True)

    def __str__(self):
        return self.user.username

class PartnerQuest(models.Model):
    partner1 = models.ForeignKey(User, related_name='partner1', on_delete=models.CASCADE)
    partner2 = models.ForeignKey(User, related_name='partner2', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    size = models.IntegerField(default=10*25*60) # 10 pomodoros
    partner1_progress = models.IntegerField(default=0)  # Progress in seconds
    partner2_progress = models.IntegerField(default=0)  # Progress in seconds

    is_completed = models.BooleanField(default=False)

    def add_progress(self, user, seconds):
        if user == self.partner1:
            self.partner1_progress += seconds
        elif user == self.partner2:
            self.partner2_progress += seconds
        if self.partner1_progress + self.partner2_progress >= self.size:
            self.is_completed = True
        self.save()

    def is_open(self):
        return not self.is_completed and timezone.now() < self.end_time

    def is_active(self):
        return timezone.now() < self.end_time

    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = timezone.now()
        if not self.end_time:
            self.end_time = self.start_time + timedelta(hours=72)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.partner1.username} + {self.partner2.username} Partner Quest"
    
class PartnerQuestRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_partner_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_partner_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(default=10*25*60) # 10 pomodoros

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"


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


class EventCondition(models.Model):
    CONDITION_TYPES = [
        ('all_completed', 'All of the specified events must be completed'),
        ('any_completed', 'Any of the specified events must be completed'),
        ('none_completed', 'None of the specified events must be completed'),
        ('time_based', 'Triggered within a specific time span'),
        ('state_based', 'Triggered based on player state'),
    ]

    name = models.CharField(max_length=255)
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPES)
    events = models.ManyToManyField('Event', blank=True, related_name='condition_events')
    required_count = models.IntegerField(default=1)  # Number of required events to be completed (for 'any_completed' type)
    start_time = models.TimeField(null=True, blank=True)  # Start time for time-based condition
    end_time = models.TimeField(null=True, blank=True)  # End time for time-based condition
    required_state = models.CharField(max_length=255, null=True, blank=True)  # Required player state (for 'state_based' type)

    def __str__(self):
        return f"Condition: {self.name} ({self.condition_type})"

    def is_met(self, player_state):
        if self.condition_type == 'all_completed':
            return all(event in player_state.completed_events.all() for event in self.events.all())
        elif self.condition_type == 'any_completed':
            return player_state.completed_events.filter(id__in=self.events.all()).count() >= self.required_count
        elif self.condition_type == 'none_completed':
            return not player_state.completed_events.filter(id__in=self.events.all()).exists()
        elif self.condition_type == 'time_based':
            current_time = timezone.now().time()
            return self.start_time <= current_time <= self.end_time
        elif self.condition_type == 'state_based':
            return self.required_state in player_state.current_state
        return False

class EventOutcome(models.Model):
    OUTCOME_TYPES = [
        ('add_points', 'Add Points'),
        # more to come
    ]
    name  = models.CharField(max_length=255)
    outcome_type = models.CharField(max_length=50, choices=OUTCOME_TYPES)
    def __str__(self):
        return f"Outcome: {self.name} ({self.outcome_type})"

    def apply(self, player_state):
        if self.outcome_type == 'add_points':
            pass
        player_state.save()

class Event(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField()  # Story text
    info_box_btn_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # Location name

    pre_timer_text = models.TextField(blank=True, null=True)
    post_timer_text = models.TextField(blank=True, null=True)
    
    #Event is completed direct or after a timer
    completion_type = models.CharField(max_length=50, blank=True, null=True, choices=[('direct','direct'),('25','25')], default='direct')
    repeatable = models.BooleanField(default=False)
    
    conditions = models.ManyToManyField(EventCondition, blank=True, related_name='events_of_condition')
    outcomes = models.ManyToManyField(EventOutcome, blank = True, related_name='events_with_outcome')
   

    def __str__(self):
        return f"Event: {self.name} at {self.location.name}"

        # Add any logic to determine if this event can be triggered
    def can_be_triggered(self, player_state):
        # Check if the event has been completed by the player
        if not self.repeatable and self in player_state.completed_events.all():
            return False
        for condition in self.conditions.all():
            if not condition.is_met(player_state):
                return False
        return True

    def apply_outcomes(self,player_state):
        for outcome in self.outcomes.all():
            outcome.apply(player_state)

class PlayerState(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)

    current_streak = models.IntegerField(default=0)
    highest_streak = models.IntegerField(default=0)
    


    
    # Many-to-many field for tracking which events the player has completed
    completed_events = models.ManyToManyField(Event, blank=True, null=True)  # Events the player has completed

    def __str__(self):
        return self.player.username

    def get_highest_streak(self):
        return self.highest_streak

    def get_streak(self):
        # Get all Pomodoros completed by the user, ordered by date
        pomodoros = Timers.objects.filter(user=self.player).order_by('-date_completed')

        if not pomodoros.exists():
            return 0  # No pomodoros, so no streak

        # Initialize streak and today's date
        today = timezone.now().date()
        timers_today = Timers.objects.filter(user=self.player, date_completed=today)
        yesterday = today - timedelta(1)
        timers_yesterday = Timers.objects.filter(user=self.player, date_completed=yesterday)

        if len(timers_today)==0 and len(timers_yesterday)==0:
            self.current_streak=0
            self.save()
            return 0
        else:
            return self.current_streak

    def update_streak(self):
        
        today = timezone.now().date()
        timers_today = Timers.objects.filter(user=self.player, date_completed=today)
        yesterday = today - timedelta(1)
        timers_yesterday = Timers.objects.filter(user=self.player, date_completed=yesterday)

        if len(timers_today)==0:
            if len(timers_yesterday)==0:
                self.current_streak=0
            self.current_streak += 1
            if self.current_streak > self.highest_streak:
                self.highest_streak = self.current_streak
        self.save()


    
    def get_total_pomos_today(self):
        # Get the current date
        today = timezone.now().date()
        # Get all Pomodoros completed by the user today
        timers_today = Timers.objects.filter(user=self.player, date_completed=today)
        # Count how many Pomodoros have been completed today
        total_pomodoros_today = len(timers_today)
        return total_pomodoros_today

    def get_total_pomos(self): 
        # Get all Pomodoros completed by the user (no date filter for all-time total)
        timers_alltime = Timers.objects.filter(user=self.player)
        # Sum the total number of Pomodoros completed all-time
        total_pomodoros_alltime = len(timers_alltime)
        return total_pomodoros_alltime

class AchievementCondition(models.Model):
    CONDITION_TYPES = [
        
    ]

    def is_met(self,player_state):
        return True

class Achievement(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    streak_required = models.IntegerField(null=True, blank=True)  # For streak-based achievements
    pomodoros_required = models.IntegerField(null=True, blank=True)  # For Pomodoro-based achievements
    page_count_required = models.IntegerField(null=True, blank=True)  # For page count milestones
    hours_a_day_required = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class AchievementCompletion(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    time_completed = models.TimeField(auto_now_add=True, null=True,blank=True)  # Time when the timer was completed

class Reward(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.IntegerField()  # Cost in points
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    claimed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Balance(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player}'s Points"
