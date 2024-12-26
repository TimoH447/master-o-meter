from django.urls import path
from .views import pomodoro_timer, login, signup, logout, timer_complete, game,get_location_story, update_player_state, trophy_room, claim_reward

urlpatterns = [
    path('timer/', pomodoro_timer, name='pomodoro_timer'),
    path('', game, name="game"),
    path('trophy-room/', trophy_room, name="trophy_room"),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('timer-complete/', timer_complete, name='timer_complete'),
    path('api/get_location_story/<str:location_name>/', get_location_story, name='get_location_story'),
    path('api/update_player_state/', update_player_state, name='update_player_state'),
    path('api/claim_reward/<int:reward_id>/', claim_reward, name='claim_reward'),
]