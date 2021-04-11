from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import CreateUserForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.utils import timezone
import datetime
from django.db.models import Sum


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
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

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


def profile(request):
    workout_list = request.user.workout_set.filter(
        date__gt=timezone.now()
    ).order_by('date')[:5]

    return render(request, 'hoosactive/profile.html', {
        'workout_list': workout_list,
        'workout_blank': range(0,5-workout_list.count())
    })

class LeaderboardView(generic.TemplateView):
    template_name = 'hoosactive/leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        context['exercise_list'] = Exercise.objects.order_by('name')
        return context

def exercise_leaderboard(request, exercise_name, sort, timeframe):
    exercise = get_object_or_404(Exercise, name=exercise_name)

    timedict = {"day": 1,"week": 7,"month": 28}

    # The following uses Django Aggregation #
    # Docs => https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#values #
    # Extra Help => https://stackoverflow.com/questions/50052902/combine-2-object-of-same-model-django #

    entry_list = Entry.objects.filter(
        exercise=exercise.id
    ).filter(
        date__gte=timezone.now()-datetime.timedelta(days=timedict[timeframe])
    ).values(
        'user'
    ).annotate(
        total_cals=Sum('calories'),
        total_time=Sum('duration_hours'),
    )

    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'exercise': exercise,
        'entry_list': entry_list,
        'timeframe': timeframe,
    })
