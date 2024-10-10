from django.contrib import admin
from .models import Timers, Location, PlayerState, Event


class TimersAdmin(admin.ModelAdmin):
    readonly_fields = ('time_completed',)

class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


# Register your models here.
admin.site.register(Timers, TimersAdmin)
admin.site.register(Location)
admin.site.register(PlayerState)
admin.site.register(Event, EventAdmin)