import json

from django.shortcuts import render, redirect
from .models import Timers
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db import models

# views.py
from django.http import JsonResponse
from django.utils import timezone

def timer_complete(request):
    if request.method == "POST":
        data = json.loads(request.body)
        duration = data.get('duration')

        # Save the timer completion in the database
        Timers.objects.create(
            user=request.user,
            duration=duration,
            date_completed=timezone.now().date(),  # Save the current date
        )

        return JsonResponse({'status': 'success', 'message': f'Timer completed: {duration} pomodoro(s)'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def pomodoro_timer(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Handle unauthenticated user, e.g., redirect to login or show a message
        return render(request, 'pomo/pomodoro.html', {
            'total_pomos_alltime': 0,
            'username': 'Guest',  # or provide an empty string
            'total_pomodoros_today': 0
        })

    user = request.user
    # Get the current date
    today = timezone.now().date()
    # Get all Pomodoros completed by the user today
    timers_today = Timers.objects.filter(user=user, date_completed=today)
    # Count how many Pomodoros have been completed today
    total_pomodoros_today = timers_today.aggregate(total=models.Sum('duration'))['total'] or 0

    # Get all Pomodoros completed by the user (no date filter for all-time total)
    timers_alltime = Timers.objects.filter(user=user)
    # Sum the total number of Pomodoros completed all-time
    total_pomodoros_alltime = timers_alltime.aggregate(total=models.Sum('duration'))['total'] or 0
    
    # Render the template with the number of Pomodoros completed today
    return render(request, 'pomo/pomodoro.html', {
        'total_pomos_alltime': total_pomodoros_alltime,
        'username': user.username,
        'total_pomodoros_today': total_pomodoros_today
    })

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=email).exists():
            user = auth.authenticate(username=email, password=password)
            print(user)
            if user is not None:
                auth.login(request, user)
                return redirect('pomodoro_timer')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect("login")
        else:
            messages.info(request, "Invalid email or password")
            return redirect('login')
    else:
        return render(request, 'pomo/login.html')


def signup(request):
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(first_name=name).exists():
            messages.info(request, "Username already taken")
            return redirect('signup')
        elif User.objects.filter(username=email).exists():
            messages.info(request, "Email already taken")
            return redirect('signup')
        else:
            user = User.objects.create_user(first_name=name,
                                            username=email,
                                            password=password)
            print(user)
            print("User registered Successfully")
            user.save()
            return redirect('login')
    else:
        return render(request, 'pomo/signup.html')

def logout(request):
    auth.logout(request)
    return redirect('pomodoro_timer')
