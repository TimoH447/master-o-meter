import json

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Timers
from .streak import calculate_streak

from django.contrib.auth.decorators import login_required
from .models import PlayerState, Location, Event
from .models import PlayerState, Reward, Balance


@login_required 
def trophy_room(request):
    try:
        # Fetch the player's state (this assumes a PlayerState model linked to the user)
        player_state = PlayerState.objects.get(player=request.user)

        # Extract relevant stats
        current_streak = player_state.get_streak()
        pomodoros_today = player_state.get_total_pomos_today()
        total_pomodoros = player_state.get_total_pomos()

        stats_context = {
            'pomodoros_today': pomodoros_today,
            'total_pomodoros': total_pomodoros,
            'streak': current_streak,
        }
    except PlayerState.DoesNotExist:
        # Handle missing player state with default values
        stats_context = {
            'pomodoros_today': 0,
            'total_pomodoros': 0,
            'streak': 0,
        }

    try:
        # Fetch user's balance, if it doesn't exist, create a new one
        balance = Balance.objects.get(player=request.user)

    except Balance.DoesNotExist:
        # Create a new balance for the user with 0 points
        balance = Balance.objects.create(player=request.user, points=0)

    # Fetch rewards associated with the player
    unclaimed_rewards = Reward.objects.filter(player=request.user, claimed=False)
    claimed_rewards = Reward.objects.filter(player=request.user, claimed=True)

    rewards_context = {
        'balance': balance,
        'unclaimed_rewards': unclaimed_rewards,
        'claimed_rewards': claimed_rewards,
    }

    # Merge both contexts
    context = {**stats_context, **rewards_context}
    return render(request, 'pomo/trophy_room.html', context)

@login_required
def claim_reward(request, reward_id):
    if request.method == "POST":
        # Get the reward object, or return a 404 if not found
        reward = get_object_or_404(Reward, id=reward_id)

        # Get the user's balance
        balance = get_object_or_404(Balance, player=request.user)

        # Check if the user has enough points to claim the reward
        if balance.points < reward.cost:
            return JsonResponse({'success': False, 'error': 'Insufficient points to claim this reward.'})

        # Deduct the cost of the reward from the user's balance
        balance.points -= reward.cost
        balance.save()

        # Mark the reward as claimed
        reward.claimed = True  # Uncomment if you add this field
        reward.save()

        # Optionally, you could log this action or send a notification

        return JsonResponse({'success': True, 'message': 'Reward claimed successfully!'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

def generate_story(location, player_state,events):
    # Filter the events based on whether they can be triggered
    valid_events = [event for event in events if event.can_be_triggered(player_state)]
    
    # Return the last valid event, if any
    if valid_events:
        selected_event = valid_events[-1]  # Example: picking the last valid event
        event_data = {
            'id': selected_event.id,
            'name': selected_event.name,
            'description': selected_event.description,
            'completion_type': selected_event.completion_type
        }
    else:
        event_data = None
    storyBox = {
        'location': location.title,
        'story_content': event_data['description'] if event_data else "Nothing interesting happens here.",
        'event': event_data,
    }
    return storyBox

@login_required
def get_location_story(request, location_name):
    try:
        # Get the location
        location = Location.objects.get(name=location_name)
        
        # Get the player state (assuming request.user is authenticated)
        player_state = PlayerState.objects.get(player=request.user)

        # Get all events for this location
        events = Event.objects.filter(location=location)
        
        storyBox = generate_story(location, player_state, events)
        return JsonResponse(storyBox)

    except Location.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)
    except PlayerState.DoesNotExist:
        return JsonResponse({'error': 'Player state not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# views.py
def update_player_state(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('event_id')  # Current event ID (if needed)
            
            # Assuming user is authenticated and we have access to player state
            player_state = PlayerState.objects.get(player=request.user)
            
            # Unlock the event (add the event to the completed or unlocked list)
            completed_event = Event.objects.get(id=event_id)
            player_state.completed_events.add(completed_event)

            # Save player state
            player_state.save()

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

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

        # Check if the user has a balance, if not, create one
        try:
            balance = Balance.objects.get(player=request.user)
        except Balance.DoesNotExist:
            balance = Balance.objects.create(player=request.user, points=0)

        # Check if this is the first Pomodoro of the day
        today = timezone.now().date()
        is_first_pomodoro_today = not Timers.objects.filter(user=request.user, date_completed=today).exists()

        # Points logic: If it's the first Pomodoro of the day, give 2 points, else give 1 point
        points_to_add = 2 if is_first_pomodoro_today else 1

        # Update the user's balance
        balance.points += points_to_add
        balance.save()

        return JsonResponse({'status': 'success', 'message': f'Timer completed: {duration} pomodoro(s)', 'points_added': points_to_add})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def game(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Handle unauthenticated user, e.g., redirect to login or show a message
        return render(request, 'pomo/start.html', {
            'total_pomos_alltime': 0,
            'username': 'Guest',  # or provide an empty string
            'total_pomodoros_today': 0
        })

    user = request.user

    """
    player_state= PlayerState.objects.get(player=user)
    location_states = LocationState.objects.filter(player=user)

    # Serialize player and location states to JSON
    player_state_json = json.dumps({
        'intelligence': player_state.intelligence,
        'retrieved_scroll': player_state.retrieved_scroll,
        'relationship_with_arlin': player_state.relationship_with_arlin,
        # Add more fields as needed
    })

    location_states_json = json.dumps(list(location_states.values()))
    """

    # Get the current date
    # Get all Pomodoros completed by the user today
    # Count how many Pomodoros have been completed today
    today = timezone.now().date()
    timers_today = Timers.objects.filter(user=user, date_completed=today)
    total_pomodoros_today = timers_today.aggregate(total=models.Sum('duration'))['total'] or 0

    timers_alltime = Timers.objects.filter(user=user)
    total_pomodoros_alltime = timers_alltime.aggregate(total=models.Sum('duration'))['total'] or 0
    # Calculate the user's streak
    streak = calculate_streak(user)

    # Pass serialized states to the template
    context = {
        #'player_state_json': player_state_json,
        #'location_states_json': location_states_json, 
        'total_pomos_alltime': total_pomodoros_alltime,
        'username': user.username,
        'streak': streak,
        'total_pomodoros_today': total_pomodoros_today,
        }
    # Render the template with the number of Pomodoros completed today
    return render(request, 'pomo/start.html', context)


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

    # Calculate the user's streak
    streak = calculate_streak(user)

    # Render the template with the number of Pomodoros completed today
    return render(request, 'pomo/pomodoro.html', {
        'total_pomos_alltime': total_pomodoros_alltime,
        'username': user.username,
        'total_pomodoros_today': total_pomodoros_today,
        'streak': streak,
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
                return redirect('game')
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
    return redirect('game')
