from django.db import models
from django.contrib.auth.models import User

class DailyProgress(models.Model):
    date = models.DateField(auto_now_add=True)  # Automatically sets the current date
    words = models.PositiveIntegerField()  # Only allows non-negative numbers
    pages = models.PositiveIntegerField()  # Only allows non-negative numbers
    cites = models.PositiveIntegerField()
    inlines = models.PositiveIntegerField()
    equations = models.PositiveIntegerField()
    figures = models.PositiveIntegerField()
    person = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to a Django user

    def __str__(self):
        return f"{self.person.username} - {self.date}"
