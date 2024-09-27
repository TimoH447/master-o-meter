from django.urls import path
from .views import pomodoro_timer, login, signup, logout, add, delete

urlpatterns = [
    path('', pomodoro_timer, name='pomodoro_timer'),
    path('login/', login, name='login'),
    #path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('add/<int:id>', add, name="add"),
    path('delete/<str:id>/', delete, name="delete"),
]