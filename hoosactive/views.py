from django.core import serializers
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.views import generic
from django.template import loader

from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .decorators import created_profile
from .forms import CreateUserForm, PostForm, ChangePictureForm
from .models import *

import datetime

def index(request):
    user = request.user
    try:
        user.profile
    except:
        recent_entries = []
        workout_list = []
        count = 0
    else:
        recent_entries = user.profile.get_recent_entries()
        workout_list = user.profile.get_upcoming_workouts()
        count = workout_list.count()
    return render(request, 'hoosactive/index.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'recent_entries': recent_entries,
        'redirect': 'index',
        'workout_blank': range(0,5-count),
        'workout_list': workout_list
    })

def log_exercise(request, redir):
    user = request.user
    if (user.is_authenticated):
        try:
            user.profile
        except:
            return HttpResponseRedirect('/profile/'+user.username+'/create/')
        else:
            if request.method == 'POST':
                exer = Exercise.objects.get(name=request.POST['drop'])
                user.profile.add_exercise(exer.name)

                # calories_burned min/max
                calories_burned = max(0, int(request.POST['calories_burned']))
                calories_burned = min(9999, calories_burned)

                # duration min/max
                duration = max(0.00, round(float(request.POST['duration'])),2)
                duration = min(99.99, round(float(request.POST['duration'])),2)

                entry = Entry.objects.create_entry(user,user.username,user.profile.city,exer,request.POST['date'],calories_burned,duration)
                return redirect('hoosactive:'+redir)
    else:
        return redirect('hoosactive:login')

def schedule_workout(request, redir):
    user = request.user
    if (user.is_authenticated):
        if request.method == 'POST':
            workout = Workout.objects.schedule_workout(user,request.POST['description'],request.POST['date'])
            return redirect('hoosactive:'+redir)
    else:
        return redirect('hoosactive:login')

def register(request):
    if request.user.is_authenticated:
        return redirect('hoosactive:index')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + username)
                return redirect('hoosactive:login')

        return render(request, 'hoosactive/register.html', {'form': form})


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

        return render(request, 'hoosactive/login.html', {})

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
                return HttpResponseRedirect('/profile/'+request.user.username+'/create/')
            else:
                return redirect('hoosactive:index')
        else:
            picture_form = ChangePictureForm(instance=profile_user.profile)
            if request.method == 'POST':
                picture_form = ChangePictureForm(request.POST, request.FILES, instance=profile_user.profile)
                if picture_form.is_valid():
                    picture_form.save()

            stat_dict = {}
            max_cals = 0
            cals_burned = 0

            for i in range(0,7):
                date = timezone.now()-datetime.timedelta(days=6-i)
                day_of_week = date.strftime('%a')
                dm_format = date.strftime('%m') + '/' + date.strftime('%d')

                aggregate = Entry.objects.filter(
                    user=profile_user.id
                ).filter(
                    date__day=date.day
                ).filter(
                    date__month=date.month
                ).filter(
                    date__year=date.year
                ).values(
                    'username',
                ).annotate(
                    total_cals=Sum('calories'),
                )

                if (aggregate.count() != 0):
                    cals_burned = int(aggregate[0]['total_cals'])
                    stat_dict[day_of_week] = (cals_burned, dm_format)
                    max_cals = max(cals_burned, max_cals)
                else:
                    stat_dict[day_of_week] = (0, dm_format)

            workout_list = profile_user.profile.get_upcoming_workouts()

            return render(request, 'hoosactive/profile.html', {
                'exercise_list': Exercise.objects.order_by('name'),
                'is_friend': authenticated_user.profile.is_friends_with(profile_user),
                'is_requested': profile_user.profile.requested_by(authenticated_user),
                'max_cals': max_cals,
                'picture_form': picture_form,
                'profile_user': profile_user,
                'recent_entries': authenticated_user.profile.get_recent_entries(),
                'redirect': 'profile_noname',
                'workout_blank': range(0,5-workout_list.count()),
                'workout_list': workout_list,
                'show_stats': profile_user.profile.show_stats,
                'stat_dict': stat_dict
            })
    else:
        return redirect('hoosactive:login')

def friends(request, username):
    return HttpResponseRedirect("/profile/"+username+"/friends/all/")

def friends_error(request, username, error):
    authenticated_user = request.user
    profile_user = User.objects.get(username=username)

    error_message = False
    if error == "nouserfound":
        error_message = True

    if authenticated_user.is_authenticated:
        try:
            profile_user.profile
        except:
            if (authenticated_user == profile_user):
                return HttpResponseRedirect('/profile/'+request.user.username+'/create/')
            else:
                return redirect('hoosactive:index')
        else:
            return render(request, "hoosactive/friends.html", {
                'error_message': error_message,
                'friends_list': profile_user.profile.friends.all(),
                'request_count': profile_user.profile.friend_requests.count(),
                'request_list': authenticated_user.profile.friend_requests.all(),
                'show_requests': (authenticated_user == profile_user),
            })
    else:
        return redirect('hoosactive:login')

def send_request(request, username, user2):
    sender = request.user
    # Make sure requesting user is logged in
    if (sender.is_authenticated):
        # Try to grab the requested user's profile
        try:
            recipient = User.objects.get(username=user2)
            prof = recipient.profile
        # If exception raised, redirect to requesting user's profile
        except:
            return HttpResponseRedirect('/profile/'+username)
        # Else, send friend request if requested user is not already a friend
        else:
            if recipient not in sender.profile.friends.all():
                if sender not in recipient.profile.friend_requests.all():
                    prof.friend_requests.add(sender)
            return HttpResponseRedirect('/profile/'+recipient.username)
    # If requesting user not logged in, redirect to login
    else:
        return redirect('hoosactive:login')

def request_response(request, username, user2, action):
    responding_user = request.user

    if (responding_user.is_authenticated):
        # Try to grab the requesting user's profile
        try:
            requesting_user = User.objects.get(username=user2)
            prof = requesting_user.profile
        # If exception raised, redirect to responding user's profile
        except:
            return HttpResponseRedirect('/profile/'+username)
        # Else, send friend request if requesting user is not already a friend
        else:
            if requesting_user in responding_user.profile.friend_requests.all():
                if (action == "accept"):
                    responding_user.profile.friends.add(requesting_user)
                    requesting_user.profile.friends.add(responding_user)
                    responding_user.profile.friend_requests.remove(requesting_user)
                elif (action == "reject"):
                    responding_user.profile.friend_requests.remove(requesting_user)
            return HttpResponseRedirect('/profile/'+username+'/friends/')
    # If responding user not logged in, redirect to index
    else:
        return redirect('hoosactive:login')

def remove_friend(request, username, user2):
    removing_user = request.user
    if (removing_user.is_authenticated):
        try:
            removed_user = User.objects.get(username=user2)
            prof = removed_user.profile
        # If exception raised, redirect to requesting user's profile
        except:
            return HttpResponseRedirect('/profile/'+username)
        # Else, attempt to remove friend
        else:
            # Only remove friend if they are already a friend
            if removed_user in removing_user.profile.friends.all():
                prof.friends.remove(removing_user)
                removing_user.profile.friends.remove(removed_user)
            return HttpResponseRedirect('/profile/'+removed_user.username)

    else:
        return redirect('hoosactive:login')

def create(request, username):
    user = request.user
    if (username != user.username):
        return HttpResponseRedirect('/profile/'+username)
    form = PostForm()
    if user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                show_stats = 'show_stats' in request.POST
                bio_text = request.POST['bio_text'].replace("\'", "’").replace("\"", '“')
                if (Profile.objects.filter(user=user).count() == 0):
                    Profile.objects.create_profile(user,request.POST['age'],request.POST['height_feet'],request.POST['height_inches'],request.POST['weight_lbs'],bio_text,request.POST['city'],request.POST['state'],show_stats)
                else:
                    Profile.objects.filter(user=user).update(age=request.POST['age'],height_feet=request.POST['height_feet'],height_inches=request.POST['height_inches'],
                    weight_lbs=request.POST['weight_lbs'],bio_text=bio_text,city=request.POST['city'],state=request.POST['state'],show_stats=show_stats)
                    Profile.objects.get(user=user).update_city()
                return HttpResponseRedirect('/profile/'+request.user.username)

        return render(request, 'hoosactive/create.html', {'form': form})
    else:
        return redirect('hoosactive:login')


def leaderboard(request):
    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'timeframe': 'day'
    })


def exercise_leaderboard(request, exercise_name, sort, timeframe, population):
    exercise = get_object_or_404(Exercise, name=exercise_name)

    timedict = {"day": 1,"week": 7,"month": 28}

    # The following uses Django Aggregation #
    # Docs => https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#values #
    # Extra Help => https://stackoverflow.com/questions/50052902/combine-2-object-of-same-model-django #

    sortdict = {
        'duration_hours': 'total_time',
        'calories': 'total_cals'
    }

    friends_list = [request.user]
    try:
        request.user.profile
    except:
        pass
    else:
        for friend in request.user.profile.friends.all():
            friends_list.append(friend)

    entry_list = Entry.objects.filter(exercise=exercise.id).filter(date__lte=timezone.now())

    if (population=="friends"):
        entry_list = entry_list.filter(user__in=friends_list)

    entry_list = entry_list.filter(
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
        'population': population
    })


def search(request):
    try:
        profile_user = User.objects.get(username=request.GET['search_profile'])
    except:
        return HttpResponseRedirect('/profile/'+request.user.username+"/friends/nouserfound/")
    else:
        try:
            profile_user.profile
        except:
            return HttpResponseRedirect('/profile/'+request.user.username+"/friends/")
        else:
            return HttpResponseRedirect('/profile/'+profile_user.username)
