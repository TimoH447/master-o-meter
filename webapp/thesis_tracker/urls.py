from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/track-progress/', views.api_track_progress, name='api_track_progress'),
]