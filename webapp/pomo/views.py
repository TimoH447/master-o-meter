from django.shortcuts import render, redirect
from .models import Timers
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from .forms import PomodoroForm
from django.db.models import Sum, F, ExpressionWrapper, fields

# views.py

def pomodoro_timer(request):
  timers = Timers.objects.all().order_by('priority')
  form = PomodoroForm()
  
  if len(timers) == 0:
      return render(request, 'pomo/pomodromo_timer.html', {
          'form': form,
          'editable': False,
          'timers': None,
      })
  
  return render(request, 'pomo/pomodromo_timer.html', {
      'form': form,
      'editable': False,
      'timers': timers,
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

def add(request,id):
    editable = True
    if request.method == "POST":
        editable = False
        form = PomodoroForm(request.POST)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.uuid = id
            form_instance.save()
            return redirect("pomodoro_timer")
    else:
        form = PomodoroForm()
        timers = Timers.objects.all()
        return render(request, 'pomo/pomodromo_timer.html', {
            'form': form,
            "editable": editable,
            'timers': timers
        })


def delete(request, id):
    timers = Timers.objects.get(id=id)
    timers.delete()
    print("Successfully Deleted {{id}}")
    timers = Timers.objects.all()
    form = PomodoroForm()
    if len(timers) == 0:
        return render(request, 'pomo/pomodromo_timer.html', {
            'form': form,
            "editable": False,
            'timers': None
        })
    return render(request, 'pomo/pomodromo_timer.html', {
        'form': form,
        "editable": False,
        'timers': timers
    })
