from django.db import models
from django.contrib.auth.models import User

class DailyProgress(models.Model):
    date = models.DateField(auto_now_add=True)  # Automatically sets the current date
    words = models.PositiveIntegerField(null=True)  # Only allows non-negative numbers
    pages = models.PositiveIntegerField(null=True)  # Only allows non-negative numbers
    inlines = models.PositiveIntegerField(null=True)
    equations = models.PositiveIntegerField(null=True)
    figures = models.PositiveIntegerField(null=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to a Django user

    def __str__(self):
        return f"{self.person.username} - {self.date}"
