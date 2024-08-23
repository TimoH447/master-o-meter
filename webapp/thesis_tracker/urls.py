from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/track-progress/', views.APITrackProgress.as_view(), name='api_track_progress'),
]