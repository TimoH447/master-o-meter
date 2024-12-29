from django.contrib import admin
from .models import Timers, Location, PlayerState, Event, Profile
from .models import Reward, Balance


class TimersAdmin(admin.ModelAdmin):
    readonly_fields = ('time_completed',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'completion_type', 'repeatable')
    search_fields = ('name', 'description')
    list_filter = ('location', 'completion_type', 'repeatable')


# Register your models here.
admin.site.register(Timers, TimersAdmin)
admin.site.register(Location)
admin.site.register(PlayerState)
admin.site.register(Event, EventAdmin)
admin.site.register(Reward)
admin.site.register(Balance)
admin.site.register(Profile)