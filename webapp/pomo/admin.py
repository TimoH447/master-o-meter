from django.contrib import admin
from .models import Timers, Location, PlayerState, Event
from .models import Reward, Balance


class TimersAdmin(admin.ModelAdmin):
    readonly_fields = ('time_completed',)

class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


# Register your models here.
admin.site.register(Timers, TimersAdmin)
admin.site.register(Location)
admin.site.register(PlayerState)
admin.site.register(Event, EventAdmin)
admin.site.register(Reward)
admin.site.register(Balance)