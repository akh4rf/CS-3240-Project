from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import CreateUserForm, PostForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.utils import timezone
import datetime
from django.db.models import Sum
from .decorators import created_profile

def index(request):
    if (request.user.is_authenticated):
        workout_list = request.user.workout_set.filter(
            date__gt=timezone.now()
        ).order_by('date')[:5]
        count = workout_list.count()
    else:
        workout_list = []
        count = 0
    return render(request, 'hoosactive/index.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'workout_list': workout_list,
        'workout_blank': range(0,5-count)
    })

def log_exercise(request):
    user = request.user
    if request.method == 'POST':
        exer = Exercise.objects.get(name=request.POST['drop'])
        entry = Entry.objects.create_entry(user,exer,request.POST['date'],request.POST['calories_burned'],request.POST['duration'])
        return redirect('hoosactive:index')

def schedule_workout(request):
    user = request.user
    if request.method == 'POST':
        workout = Workout.objects.schedule_workout(user,request.POST['description'],request.POST['date'])
        return redirect('hoosactive:index')

def register(request):
    if request.user.is_authenticated:
        return redirect('hoosactive:index')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user =form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + username)

                return redirect('hoosactive:login')

        context = {'form': form}
        return render(request, 'hoosactive/register.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('hoosactive:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('hoosactive:index')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'hoosactive/login.html', context)

def profile_noname(request):
    return HttpResponseRedirect('/profile/'+request.user.username)

def profile(request, username):
    authenticated_user = request.user
    profile_user = User.objects.get(username=username)

    if authenticated_user.is_authenticated:
        try:
            profile_user.profile
        except:
            if (authenticated_user == profile_user):
                return redirect('hoosactive:create')
            else:
                return redirect('hoosactive:index')
        else:
            workout_list = profile_user.workout_set.filter(
                date__gt=timezone.now()
            ).order_by(
                'date'
            )[:5]

            is_friend = False
            if profile_user in authenticated_user.profile.friends.all():
                is_friend = True

            return render(request, 'hoosactive/profile.html', {
              'workout_list': workout_list,
              'workout_blank': range(0,5-workout_list.count()),
              'profile_user': profile_user,
              'is_friend': is_friend
            })
    else:
        return redirect('hoosactive:login')


def create(request):
    user = request.user
    form = PostForm()
    if user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                Profile.objects.create_profile(user,request.POST['age'],request.POST['height_feet'],request.POST['height_inches'],request.POST['weight_lbs'],request.POST['bio_text'],request.POST['city'],request.POST['state'])
                return HttpResponseRedirect('/profile/'+request.user.username)

        context = {'form': form}
        return render(request, 'hoosactive/create.html', context)
    else:
        return redirect('hoosactive:index')


def leaderboard(request):
    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'timeframe': 'day'
    })


def exercise_leaderboard(request, exercise_name, sort, timeframe):
    exercise = get_object_or_404(Exercise, name=exercise_name)

    timedict = {"day": 1,"week": 7,"month": 28}

    # The following uses Django Aggregation #
    # Docs => https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#values #
    # Extra Help => https://stackoverflow.com/questions/50052902/combine-2-object-of-same-model-django #

    sortdict = {
        'duration_hours': 'total_time',
        'calories': 'total_cals'
    }

    entry_list = Entry.objects.filter(
        exercise=exercise.id
    ).filter(
        date__gte=timezone.now()-datetime.timedelta(days=timedict[timeframe])
    ).values(
        'username',
        'city'
    ).annotate(
        total_cals=Sum('calories'),
        total_time=Sum('duration_hours'),
    ).order_by(
        '-'+sortdict[sort]
    )

    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'exercise': exercise,
        'entry_list': entry_list,
        'timeframe': timeframe,
    })
