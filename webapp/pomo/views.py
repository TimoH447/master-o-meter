import json
from datetime import timedelta
import logging

# Get an instance of a logger
logger = logging.getLogger('django')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import Timers
from .streak import calculate_streak

from django.contrib.auth.decorators import login_required
from .models import PlayerState, Location, Event
from .models import Reward, Balance
from .models import Profile, FriendRequest, PartnerQuest, PartnerQuestRequest
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
def accept_partner_quest(request, request_id):
    partner_quest_request = get_object_or_404(PartnerQuestRequest, id=request_id)
    if partner_quest_request.to_user == request.user:
        # Check if either user has an active PartnerQuest
        active_quests = PartnerQuest.objects.filter(
            (Q(partner1=partner_quest_request.from_user) | Q(partner2=partner_quest_request.from_user) |
             Q(partner1=partner_quest_request.to_user) | Q(partner2=partner_quest_request.to_user)) &
            Q(is_completed=False)
        )

        if any(quest.is_active() for quest in active_quests):
            messages.error(request, "Both users must finish their current partner quests before starting a new one.")
            return redirect('common_rooms')

        try:
            PartnerQuest.objects.create(
                partner1=partner_quest_request.from_user,
                partner2=partner_quest_request.to_user,
                size=partner_quest_request.size
            )
            partner_quest_request.delete()
        except Exception as e:
            logger.error(f"Error creating PartnerQuest: {e}")
            messages.error(request, "Could not create PartnerQuest.")
            return redirect('common_rooms')
    return redirect('common_rooms')

@login_required
def decline_partner_quest(request, request_id):
    partner_quest_request = get_object_or_404(PartnerQuestRequest, id=request_id)
    if partner_quest_request.to_user == request.user:
        partner_quest_request.delete()
    return redirect('common_rooms')

@login_required
def send_partner_quest_request(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    
    # Check if either user has an active PartnerQuest
    active_quests = PartnerQuest.objects.filter(
        (Q(partner1=request.user) | Q(partner2=request.user) |
         Q(partner1=friend) | Q(partner2=friend)) &
        Q(is_completed=False)
    )

    if any(quest.is_active() for quest in active_quests):
        messages.error(request, "Both users must finish their current partner quests before starting a new one.")
        return redirect('common_rooms')

    PartnerQuestRequest.objects.create(from_user=request.user, to_user=friend)
    messages.success(request, "Partner quest request sent successfully.")
    return redirect('common_rooms')

def get_context_partner_quests(user):
    """
    get the context for the partner quests
    """
    partner_quests = PartnerQuest.objects.filter(models.Q(partner1=user) | models.Q(partner2=user))
    partner_quests_requests = PartnerQuestRequest.objects.filter(models.Q(from_user=user) | models.Q(to_user=user))
    partner_quest_list=[]
    for quest in partner_quests:
        partner_quest_list.append({
            'partner1': quest.partner1.username,
            'partner2': quest.partner2.username,
            'start_time': quest.start_time,
            'end_time': quest.end_time,
            'size': quest.size //60,
            'partner1_progress': quest.partner1_progress//60,
            'partner2_progress': quest.partner2_progress//60,
            'total_progress': (quest.partner1_progress + quest.partner2_progress) // 60,
            'is_open': quest.is_open(),
        })
    request_list = []
    for request in partner_quests_requests:
        request_list.append({
            'id': request.id,
            'from_user': request.from_user.username,
            'to_user': request.to_user.username,
            'timestamp': request.timestamp,
            'size': request.size //60,
            'is_receiver': request.to_user == user,
        })
    return {'partner_quests': partner_quest_list, 'partner_quests_requests': request_list}

@login_required
def common_rooms(request):
    partner_quest_context = get_context_partner_quests(request.user)
    friends = request.user.profile.friends.all()
    friend_requests = FriendRequest.objects.filter(to_user=request.user)

    friends_info = []
    for friend in friends:
        player_state = PlayerState.objects.get(player=friend.user)
        friends_info.append({
            'id': friend.user.id,
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
    location_description  = Location.objects.get(name='common_rooms').description
    
    return render(request, 'pomo/common_rooms.html', {
        **stats, **partner_quest_context,
        'location_description': location_description,
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
            'highest_streak': 0,
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
def create_reward(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')

        # Create the reward
        Reward.objects.create(
            name=name,
            description=description,
            cost=cost,
            player=request.user
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

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
        duration_in_seconds = data.get('duration')

        # Get the current user and today's date
        user = request.user
        today = timezone.now().date()

        player_state = PlayerState.objects.get(player=user)
        player_state.update_streak()

        # Save the timer completion in the database
        Timers.objects.create(
            user=request.user,
            duration=duration_in_seconds,
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
        elif duration_in_seconds >= 25 * 60:
            points_to_add = 1
        else:
            points_to_add = 0

        # Update the user's balance
        balance.points += points_to_add
        balance.save()

        # Update partner quest progress
        partner_quests = PartnerQuest.objects.filter(
            models.Q(partner1=user) | models.Q(partner2=user),
            end_time__gte=timezone.now()
        )
        for quest in partner_quests:
            if quest.is_open():
                quest.add_progress(user, duration_in_seconds)

        # Calculate the total pomodoros today
        total_pomodoros_today = Timers.objects.filter(user=user, date_completed=today).count()
        # Calculate the user's streak
        streak = calculate_streak(user)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Timer completed: {duration_in_seconds} pomodoro(s)',
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

    player_state= PlayerState.objects.get(player=user)
    highest_streak = player_state.get_highest_streak()

    return {
        "total_pomos_alltime": total_pomodoros_alltime,
        "total_pomodoros_today": total_pomodoros_today,
        "streak": streak,
        "highest_streak": highest_streak,
    }

def get_pomo_stats_detailed(user):
    today = timezone.now().date()
    # Collect study hours for the last seven days
    weekly_study = []
    for k in range(2):
        weekly_study_time = []
        week_total_time = 0
        for i in range(7):
            j = i+7*k
            day = today - timedelta(days=j)
            timers_day = Timers.objects.filter(user=user, date_completed=day)
            total_seconds = sum(timer.duration for timer in timers_day)
            total_minutes = total_seconds // 60
            # the amount studied is including the break times, for each 25min one 5min break is added
            total_minutes += (total_seconds // 1500) * 5
            week_total_time += total_minutes/60
            weekly_study_time.append(total_minutes/60)
        past_week = {"week": k, "study_time": weekly_study_time, "hours_studied":week_total_time}
        weekly_study.append(past_week)

    stats = get_pomo_stats(user)
    return {**stats, "weeks": weekly_study}



def get_context_navbar(user):
    """
    get the context for the base template 
    """
    player_state = PlayerState.objects.get(player=user)
    context = {"streak": player_state.get_streak(),
               "total_pomodoros_today": player_state.get_total_pomos_today()}
    return context

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

def get_event_status(user,event):
    player_state = PlayerState.objects.get(player=user)
    if event in player_state.completed_events.all():
        return "completed"
    if event.can_be_triggered(player_state):
        return "open"
    else:
        return "locked"

@login_required
def event_timer(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    context  = {
        'event_status': get_event_status(user,event),
        'event_id': event_id,
        'location': event.location.title,
        'event_name': event.name,
        'pre_timer_text': event.pre_timer_text,
        'post_timer_text': event.post_timer_text,
        'repeatable': event.repeatable,
    }

    if context['event_status']=="locked":
        raise Http404("Event does not exist")

    navbar_context = get_context_navbar(request.user)

    timer = get_timer_context(request.user)
    context = {**context, **navbar_context, **timer}

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
            auth.login(request,user)
            return redirect('intro')
    else:
        return render(request, 'pomo/signup.html')

def logout(request):
    auth.logout(request)
    return redirect('game')

def start(request):
    return render(request,"pomo/start.html")

def get_available_events_context(user):
    # Get the player's state
    player_state = PlayerState.objects.get(player=user)
    # Get all events
    all_events = Event.objects.all()
    # Filter events that can be triggered
    available_events = [event for event in all_events if event.can_be_triggered(player_state)]
    return available_events


def get_completed_events_context(user):
    # Get the player's state
    try:
        player_state = PlayerState.objects.get(player=user)
    except PlayerState.DoesNotExist:
        return []

    # Get the completed events
    completed_events = player_state.completed_events.all()
    
    return completed_events    


def get_player_context(user):
    try:
        player_state = PlayerState.objects.get(player=user)
    except PlayerState.DoesNotExist:
        player_state = None

    context = {
        'user': user,
        'player': player_state,
        'number_of_friends': user.profile.friends.count(),
        'completed_events_count': player_state.completed_events.count() if player_state else 0,
    }
    return context

def get_hub_context(user):
    navbar = get_context_navbar(user)
    open_events = get_available_events_context(user)
    completed_events= get_completed_events_context(user)
    player_context = get_player_context(user)

    return {**navbar, "available_events": open_events, "completed_events": completed_events, **player_context}

@login_required
def hub(request):
    context = get_hub_context(request.user)
    return render(request,"pomo/hub.html", context)