from datetime import datetime
import json

from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import DailyProgress

@csrf_exempt  # Disable CSRF for simplicity (not recommended for production without secure measures)
def api_track_progress(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Get the fields from the JSON request
            word_count = data.get('word_count')
            page_count = data.get('page_count')
            person_username = data.get('person')  # Assume the person is identified by username

            # Find the user object by username
            person = User.objects.get(username=person_username)

            # Validate that word_count and page_count are provided
            if word_count is None or page_count is None:
                return JsonResponse({'error': 'Word count and page count are required.'}, status=400)

            # Create a new DailyProgress entry
            DailyProgress.objects.create(
                word_count=word_count,
                page_count=page_count,
                person=person
            )

            return JsonResponse({'status': 'success', 'message': 'Progress saved successfully.'})

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Create your views here.

def get_thesis_progress():
    # In a real scenario, you'd calculate or fetch these values from a database or file
    word_count = 12345  # Example: dynamic word count value
    page_count = 45     # Example: dynamic page count value
    return word_count, page_count

def index(request):
    # Get current progress (this could be fetched from the database or a file)
    word_count, page_count = get_thesis_progress()

    # Pass data to the template
    context = {
        'word_count': word_count,
        'page_count': page_count,
        'current_year': datetime.now().year,
    }

    # Render the template and pass the context
    return render(request, 'thesis_tracker/index.html', context)