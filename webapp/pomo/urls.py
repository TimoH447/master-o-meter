from django.urls import path
from .views import pomodoro_timer, login, signup, logout, timer_complete, game,get_location_info, update_player_state, trophy_room, claim_reward,event_timer

urlpatterns = [
    path('timer/', pomodoro_timer, name='pomodoro_timer'),
    path('', game, name="game"),
    path('event/<int:event_id>/', event_timer, name='event_detail'),
    path('trophy-room/', trophy_room, name="trophy_room"),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('timer-complete/', timer_complete, name='timer_complete'),
    path('api/get_location_info/<str:location_name>/', get_location_info, name='get_location_info'),
    path('api/update_player_state/', update_player_state, name='update_player_state'),
    path('api/claim_reward/<int:reward_id>/', claim_reward, name='claim_reward'),
]