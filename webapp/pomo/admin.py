from django.contrib import admin
from .models import Timers, Location, PlayerState, Event, Profile
from .models import Reward, Balance, FriendRequest, PartnerQuestRequest, PartnerQuest
from .models import EventCondition, EventOutcome
from .models import Quest, PlayerQuestProgress, QuestStep


class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')

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
admin.site.register(FriendRequest)
admin.site.register(PartnerQuestRequest)
admin.site.register(PartnerQuest)
admin.site.register(EventCondition)
admin.site.register(EventOutcome)
admin.site.register(Quest, QuestAdmin)
admin.site.register(PlayerQuestProgress)
admin.site.register(QuestStep)