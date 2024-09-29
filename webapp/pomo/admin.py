from django.contrib import admin
from .models import Timers


class TimersAdmin(admin.ModelAdmin):
    readonly_fields = ('time_completed',)

# Register your models here.
admin.site.register(Timers, TimersAdmin)