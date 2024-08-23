from datetime import datetime
import json

from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import DailyProgress

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  

class APITrackProgress(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        content = {"message": "Hello World"}
        return Response(content)

    def post(self,request):
        try:
            data = json.loads(request.body)

            # Get the fields from the JSON request
            words = data.get('words')
            pages = data.get('pages')
            figures = data.get('figures')
            inlines = data.get('inlines')
            equations = data.get('equations')
            person_username = data.get('username')

            # Validate that word_count and page_count are provided
            if words is None or pages is None:
                return Response({'error': 'Word count and page count are required.'}, status=400)

            # Find the user object by username
            user = User.objects.get(username=person_username)
            
            # Create a new DailyProgress entry
            day = DailyProgress(words= words, pages=pages,figures=figures,inlines=inlines,equations=equations, person=user)
            day.save()

            return Response({"user": "dit is jeck"})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data.'}, status=400)

def get_thesis_progress():
    user = User.objects.get(username='timoh')
    # Get the DailyProgress records for the logged-in user, ordered by date
    progress_data = DailyProgress.objects.filter(person=user).order_by('date')

    # Extract dates and word counts
    dates = [progress.date.strftime('%Y-%m-%d') for progress in progress_data]
    word_counts = [progress.words for progress in progress_data]
    page_counts = [progress.pages for progress in progress_data]
    inline_counts = [progress.inlines for progress in progress_data]
    equation_counts = [progress.equations for progress in progress_data]
    figure_counts = [progress.figures for progress in progress_data]


    context = {
        'dates': dates,
        'word_counts': word_counts,
        'page_counts': page_counts,
        'inline_counts': inline_counts,
        'equation_counts': equation_counts,
        'figure_counts': figure_counts,
    }


    return context

def index(request):
    # Get current progress (this could be fetched from the database or a file)
    context = get_thesis_progress()

    # Render the template and pass the context
    return render(request, 'thesis_tracker/index.html', context)

def progress_chart(request):
    user = User.objects.get(username='timoh')
    # Get the DailyProgress records for the logged-in user, ordered by date
    progress_data = DailyProgress.objects.filter(person=user).order_by('date')

    # Extract dates and word counts
    dates = [progress.date.strftime('%Y-%m-%d') for progress in progress_data]
    word_counts = [progress.words for progress in progress_data]
    page_counts = [progress.pages for progress in progress_data]
    inline_counts = [progress.inlines for progress in progress_data]
    equation_counts = [progress.equations for progress in progress_data]
    figure_counts = [progress.figures for progress in progress_data]


    context = {
        'dates': dates,
        'word_counts': word_counts,
        'page_counts': page_counts,
        'inline_counts': inline_counts,
        'equation_counts': equation_counts,
        'figure_counts': figure_counts,
    }

    return render(request, 'thesis_tracker/progress_chart.html', context)
