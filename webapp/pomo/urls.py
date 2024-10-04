from django.urls import path
from .views import pomodoro_timer, login, signup, logout, timer_complete, start

urlpatterns = [
    path('', pomodoro_timer, name='pomodoro_timer'),
    path('start/', start, name="start"),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('timer-complete/', timer_complete, name='timer_complete'),
]