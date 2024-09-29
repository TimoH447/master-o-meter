from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Timers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(default=1)  # 1 for 25 min, 2 for 50 min
    date_completed = models.DateField(default=timezone.now)  # Date when the timer was completed
    time_completed = models.TimeField(auto_now_add=True, null=True,blank=True)  # Time when the timer was completed

    def __str__(self):
        return f"{self.user.username} - {self.duration} pomodoro(s) on {self.date_completed}"

