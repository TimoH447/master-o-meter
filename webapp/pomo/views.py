import json
from datetime import timedelta

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
from .models import Reward, Balance
from .models import Profile, FriendRequest
from django.db.models import Q

@login_required
def send_friend_request(request, username):
    user = get_object_or_404(User, username=username)
    friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=user)
    return redirect('common_rooms')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        friend_request.to_user.profile.friends.add(friend_request.from_user.profile)
        friend_request.from_user.profile.friends.add(friend_request.to_user.profile)
        friend_request.delete()
    return redirect('common_rooms')

@login_required
def common_rooms(request):
    friends = request.user.profile.friends.all()
    friend_requests = FriendRequest.objects.filter(to_user=request.user)

    friends_info = []
    for friend in friends:
        player_state = PlayerState.objects.get(player=friend.user)
        friends_info.append({
            'username': friend.user.username,
            'streak': player_state.get_streak(),
            'pomodoros_today': player_state.get_total_pomos_today(),
        })
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query)).exclude(username=request.user.username)
    else:
        users = User.objects.none()

    stats = get_pomo_stats(request.user)
    
    return render(request, 'pomo/common_rooms.html', {
        **stats,
        'friends_info': friends_info,
        'friend_requests': friend_requests,
        'users': users,
        'query': query,
    })


@login_required 
def trophy_room(request):
    try:
        # Fetch the player's state (this assumes a PlayerState model linked to the user)
        player_state = PlayerState.objects.get(player=request.user)

        # Extract relevant stats
        stats  = get_pomo_stats_detailed(request.user)

    except PlayerState.DoesNotExist:
        # Handle missing player state with default values
        stats_context = {
            'total_pomodoros_today': 0,
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
    context = {**stats, **rewards_context}
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

def generate_location_info(location, player_state, events):
    valid_events = [event for event in events if event.can_be_triggered(player_state)]
    
    events_data = [{
        'id': event.id,
        'info_box_btn_name': event.info_box_btn_name,
        'info_box_description': event.description
    } for event in valid_events]
    
    locationInfoBox = {
        'location_name': location.name,
        'location': location.title,
        'location_description': location.description,
        'events': events_data
    }
    return locationInfoBox

@login_required
def get_location_info(request, location_name):
    try:
        # Get the location
        location = Location.objects.get(name=location_name)
        
        # Get the player state (assuming request.user is authenticated)
        player_state = PlayerState.objects.get(player=request.user)

        # Get all events for this location
        events = Event.objects.filter(location=location)
        
        locationInfoBox = generate_location_info(location, player_state, events)
        return JsonResponse(locationInfoBox)

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

        # Get the current user and today's date
        user = request.user
        today = timezone.now().date()

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

        # Points logic: If it's the first Pomodoro of the day, give 2 points regardless of duration,
        # if the Pomodoro is 25 minutes or longer, give 1 point, if it's less than 25 minutes, give 0 points
        if is_first_pomodoro_today:
            points_to_add = 2
        elif duration >= 25 * 60:
            points_to_add = 1
        else:
            points_to_add = 0

        # Update the user's balance
        balance.points += points_to_add
        balance.save()

        # Calculate the total pomodoros today
        total_pomodoros_today = Timers.objects.filter(user=user, date_completed=today).count()
        # Calculate the user's streak
        streak = calculate_streak(user)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Timer completed: {duration} pomodoro(s)',
            'points_added': points_to_add,
            'total_pomodoros_today': total_pomodoros_today,
            'streak': streak,})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def game(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Handle unauthenticated user, e.g., redirect to login or show a message
        return render(request, 'pomo/map.html', {
            'total_pomos_alltime': 0,
            'username': 'Guest',  # or provide an empty string
            'total_pomodoros_today': 0
        })

    user = request.user

    if request.user.is_authenticated:
        stats = get_pomo_stats(request.user)
        timer = get_timer_context(request.user)
        context = {**stats, **timer, 'username': user.username}

    # Render the template with the number of Pomodoros completed today
    return render(request, 'pomo/map.html', context)

def get_pomo_stats(user):
    # Get the current date
    today = timezone.now().date()
    # Get all Pomodoros completed by the user today
    timers_today = Timers.objects.filter(user=user, date_completed=today)
    # Count how many Pomodoros have been completed today
    total_pomodoros_today = len(timers_today)

    # Get all Pomodoros completed by the user (no date filter for all-time total)
    timers_alltime = Timers.objects.filter(user=user)
    # Sum the total number of Pomodoros completed all-time
    total_pomodoros_alltime = len(timers_alltime)
    # Calculate the user's streak
    streak = calculate_streak(user)

    return {
        "total_pomos_alltime": total_pomodoros_alltime,
        "total_pomodoros_today": total_pomodoros_today,
        "streak": streak,
    }

def get_pomo_stats_detailed(user):
    today = timezone.now().date()
    # Collect study hours for the last seven days
    study_hours_last_seven_days = []
    for i in range(7):
        day = today - timedelta(days=i)
        timers_day = Timers.objects.filter(user=user, date_completed=day)
        total_seconds = sum(timer.duration for timer in timers_day)
        total_minutes = total_seconds // 60
        # the amount studied is including the break times, for each 25min one 5min break is added
        total_minutes += (total_seconds // 1500) * 5
        study_hours_last_seven_days.append(total_minutes/60)

    stats = get_pomo_stats(user)
    return {**stats, 'study_hours_last_seven_days': study_hours_last_seven_days}



def get_context_navbar(user):
    """
    get the context for the base template 
    """
    stats = get_pomo_stats(user)
    return stats

def get_timer_context(user):
    """
    get the context for the timer template
    """
    is_developer = user.profile.is_developer
    stats = {
        "is_developer": is_developer }    
    return stats


def pomodoro_timer(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Handle unauthenticated user, e.g., redirect to login or show a message
        return render(request, 'pomo/library.html', {
            'total_pomos_alltime': 0,
            'username': 'Guest',  # or provide an empty string
            'total_pomodoros_today': 0,
            'is_developer': False
        })

    if request.user.is_authenticated:
        stats = get_pomo_stats(request.user)
        timer = get_timer_context(request.user)
        context = {**stats, **timer}


    # Render the template with the number of Pomodoros completed today
    return render(request, 'pomo/library.html', context)

def event_timer(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    context  = {
        'event_id': event_id,
        'location': event.location.title,
        'event_name': event.name,
        'pre_timer_text': event.pre_timer_text,
        'post_timer_text': event.post_timer_text,
        'repeatable': event.repeatable,
    }

    if request.user.is_authenticated:
        stats = get_pomo_stats(request.user)
        timer = get_timer_context(request.user)
        context = {**context, **stats, **timer}

    return render(request, 'pomo/event.html', 
                  context)

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

def intro(request):
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
                return redirect("intro")
        else:
            messages.info(request, "Invalid email or password")
            return redirect('intro')
    else:
        return render(request, 'pomo/intro.html')

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
            return redirect('intro')
    else:
        return render(request, 'pomo/signup.html')

def logout(request):
    auth.logout(request)
    return redirect('game')
