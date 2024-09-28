from django.urls import path
from .views import pomodoro_timer, login, signup, logout, timer_complete

urlpatterns = [
    path('', pomodoro_timer, name='pomodoro_timer'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('timer-complete/', timer_complete, name='timer_complete'),
]