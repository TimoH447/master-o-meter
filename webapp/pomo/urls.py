from django.urls import path
from .views import pomodoro_timer, login, signup, logout, timer_complete, game,get_location_info, update_player_state
from .views import trophy_room, claim_reward,event_timer
from .views import intro, accept_friend_request, send_friend_request, common_rooms
from .views import accept_partner_quest, decline_partner_quest, send_partner_quest_request
from .views import start, hub, create_reward

urlpatterns = [
    path('send_friend_request/<str:username>/', send_friend_request, name='send_friend_request'),
    path('send_partner_quest_request/<int:user_id>/', send_partner_quest_request, name='send_partner_quest_request'),
    path('accept_friend_request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('accept_partner_quest/<int:request_id>/', accept_partner_quest, name='accept_partner_quest'),
    path('decline_partner_quest/<int:request_id>/', decline_partner_quest, name='decline_partner_quest'),
    path('common_rooms/', common_rooms, name='common_rooms'),
    path('library/', pomodoro_timer, name='library'),
    path('', hub, name="game"),
    path('event/<int:event_id>/', event_timer, name='event_detail'),
    path('trophy-room/', trophy_room, name="trophy_room"),
    path('login/', login, name='login'),
    path('intro/', intro, name='intro'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('timer-complete/', timer_complete, name='timer_complete'),
    path('api/get_location_info/<str:location_name>/', get_location_info, name='get_location_info'),
    path('api/update_player_state/', update_player_state, name='update_player_state'),
    path('create_reward/', create_reward, name='create_reward'),
    path('api/claim_reward/<int:reward_id>/', claim_reward, name='claim_reward'),
    path('start/', start, name="start"),
    path('map/', game, name="map"),
]