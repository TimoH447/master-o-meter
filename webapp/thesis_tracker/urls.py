from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/track-progress/', views.APITrackProgress.as_view(), name='api_track_progress'),
    path('progress-chart/', views.progress_chart, name='progress_chart'),
    path('mehr-infos/', views.mehr_infos, name='mehr_infos'),
]