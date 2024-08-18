from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

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