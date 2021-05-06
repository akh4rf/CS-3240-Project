from django.db.models import Sum, Avg, Func
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.utils import timezone

from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
from .tokens import account_activation_token, password_reset_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views import generic
from django.template import loader

from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as auth_login

from .forms import CreateUserForm, PostForm, ChangePictureForm, UserForgotPasswordForm, UserPasswordResetForm
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
                duration = max(0.00, round(float(request.POST['duration']),2))
                duration = min(99.99, duration)

                # extra data
                extra_data = max(0.00, round(float(request.POST['extra']),2))
                extra_data = min(99.99, extra_data)

                entry = Entry.objects.create_entry(user,user.username,user.profile.city,exer,request.POST['date'],calories_burned,duration,extra_data)
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
                # Check if email has already been registered
                check_email = request.POST.get('email')
                check_user = User.objects.filter(email=check_email)
                if len( check_user ) > 0:
                    messages.add_message(request, messages.WARNING, 'This email or username has already been registered to another user')
                    return render(request, 'hoosactive/register.html',{
                        'form': form,
                        'redirect': 'index',
                    })

                user = form.save()
                user.is_active = False
                user.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + username + '. We sent you an email to activate your account')
                # Send activation email
                url = request.META['HTTP_HOST'] + '/activate/' + urlsafe_base64_encode(force_bytes(user.pk)) + '/' + account_activation_token.make_token(user)
                mes = ( 'Activate your email by clicking the following link:\n' +
                       url
                )
                send_mail( 'Activate Email for HoosActive!', mes, EMAIL_HOST_USER, [user.email] )

                return redirect('hoosactive:login')

        return render(request, 'hoosactive/register.html', {
            'form': form,
            'redirect': 'index',
        })

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        messages.add_message(request, messages.WARNING, str(e))
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # Send Welcome Email
        subj = "Welcome to HoosActive!"
        message = ( "Hey " + user.username + "!" +
                  "\n\nWelcome to the fastest growing health and fitness platform in Charlottesville! " +
                  "We look forward to seeing the progress you make toward achieving your goals! " +
                  "\n\nHappy Workouts!\nThe HoosActive Team" )
        send_mail( subj, message, EMAIL_HOST_USER, [user.email] )
    else:
        messages.add_message(request, messages.WARNING, 'Account activation link is invalid.')

    return redirect('hoosactive:index')

#https://www.youtube.com/watch?v=tUqUdu0Sjyc used the following toutrial for login and parts of registration
def login(request):
    if request.user.is_authenticated:
        return redirect('hoosactive:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_active is not False:
                auth_login(request, user)
                return redirect('hoosactive:index')
            else:
                messages.info(request, 'Username OR password is incorrect, make sure your email is activated')

        return render(request, 'hoosactive/login.html', {
            'redirect': 'index',
        })

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
                'redirect': 'index',
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
                    # Send Email to requested friend if notifications are on
                    if ( prof.receive_notifications is True ):
                        subj = "New Friend Request Received!"
                        message = ( "Hey " + recipient.username + "!" +
                                  "\n\nYou have received a new friend request from " + sender.username +
                                  "! Check out their profile at: " + request.META['HTTP_HOST'] + '/profile/' + sender.username + "/" +
                                  "\n\nHappy Workouts!\nThe HoosActive Team" )
                        send_mail( subj, message, EMAIL_HOST_USER, [recipient.email] )
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
                    # Send Email to the requesting user if notifications are on
                    if ( prof.receive_notifications is True ):
                        subj = responding_user.username + " Accepted Your Friend Request!"
                        message = ( "Hey " + requesting_user.username + "!" +
                                   "\n\n" + responding_user.username + " has accepted you friend request!" +
                                  "! Add more frineds at: " + request.META['HTTP_HOST'] + '/profile/' + requesting_user.username + "/friends/"
                                  "\n\nHappy Workouts!\nThe HoosActive Team" )
                        send_mail( subj, message, EMAIL_HOST_USER, [requesting_user.email] )
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
    if user.is_active is False:
        return HttpResponseRedirect('/activation_not_complete')

    form = PostForm()
    if user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                show_stats = 'show_stats' in request.POST
                receive_notifications = 'receive_notifications' in request.POST
                bio_text = request.POST['bio_text'].replace("\'", "’").replace("\"", '“')
                if (Profile.objects.filter(user=user).count() == 0):
                    Profile.objects.create_profile(user,request.POST['age'],request.POST['height_feet'],request.POST['height_inches'],request.POST['weight_lbs'],bio_text,request.POST['city'],request.POST['state'],show_stats,receive_notifications)
                else:
                    Profile.objects.filter(user=user).update(age=request.POST['age'],height_feet=request.POST['height_feet'],height_inches=request.POST['height_inches'],
                    weight_lbs=request.POST['weight_lbs'],bio_text=bio_text,city=request.POST['city'],state=request.POST['state'],show_stats=show_stats, receive_notifications=receive_notifications)
                    Profile.objects.get(user=user).update_city()
                return HttpResponseRedirect('/profile/'+request.user.username)

        return render(request, 'hoosactive/create.html', {
            'form': form,
            'redirect': 'index',
        })
    else:
        return redirect('hoosactive:login')

def leaderboard(request):
    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'redirect': 'index',
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
        'calories': 'total_cals',
        'extra': 'total_extra'
    }

    extra_column_dict = {
        'SpeedCardio': 'Avg Mile Time',
        'DistanceCardio': 'Distance (Miles)',
        'Bodyweight': 'Total Reps'
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
    )

    class Round0(Func):
        function = "ROUND"
        template = "%(function)s(%(expressions)s::numeric, 0)"

    class Round2(Func):
        function = "ROUND"
        template = "%(function)s(%(expressions)s::numeric, 2)"

    if (exercise.type=="SpeedCardio"):

        entry_list = entry_list.annotate(
            total_cals=Sum('calories'),
            total_time=Sum('duration_hours'),
            total_extra=Round2(Avg('extra')),
        )
    elif (exercise.type=="DistanceCardio"):

        entry_list = entry_list.annotate(
            total_cals=Sum('calories'),
            total_time=Sum('duration_hours'),
            total_extra=Round2(Sum('extra')),
        )
    elif (exercise.type=="Bodyweight"):

        entry_list = entry_list.annotate(
            total_cals=Sum('calories'),
            total_time=Sum('duration_hours'),
            total_extra=Round0(Sum('extra')),
        )

    if ((exercise.type=="SpeedCardio") and sort=="extra"):
        entry_list = entry_list.order_by(sortdict[sort])
    else:
        entry_list = entry_list.order_by('-'+sortdict[sort])

    return render(request, 'hoosactive/leaderboard.html', {
        'entry_list': entry_list,
        'exercise_list': Exercise.objects.order_by('name'),
        'exercise': exercise,
        'extra_col_title': extra_column_dict[exercise.type],
        'redirect': 'index',
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


def password_reset(request):
    if request.method == "POST":
        form = UserForgotPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            qs = User.objects.filter(email=email)

            if len(qs) > 0:
                user = qs[0]
                user.is_active = False
                user.save()


                # Send activation email
                url = request.META['HTTP_HOST'] + '/password/change/' + urlsafe_base64_encode(force_bytes(user.pk)) + '/' + account_activation_token.make_token(user)
                mes = ( 'Reset your password by clicking the following link:\n' +
                       url
                )
                send_mail( 'Reset Password for HoosActive', mes, EMAIL_HOST_USER, [user.email] )

            messages.add_message(request, messages.SUCCESS, 'Email submitted. If your email is registered you should receive an email shortly')
        else:
            messages.add_message(request, messages.WARNING, 'Email not submitted. Check email syntax')
            return render(request, 'password/reset.html', {
                'form': form,
                'redirect': 'index',
            })
    return render(request, 'password/reset.html', {
        'form': UserForgotPasswordForm,
        'redirect': 'index',
    })

def password_change(request, uidb64, token):
    if request.method == 'POST':
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.add_message(request, messages.WARNING, str(e))
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            form = UserPasswordResetForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                user.is_active = True
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Password reset successfully.')
                return redirect('hoosactive:login')
            else:
                context = {
                    'form': form,
                    'redirect': 'index',
                    'uid': uidb64,
                    'token': token
                }
                messages.add_message(request, messages.WARNING, 'Password could not be reset.')
                return render(request, 'password/change.html', context)
        else:
            messages.add_message(request, messages.WARNING, 'Password reset link is invalid.')
            messages.add_message(request, messages.WARNING, 'Please request a new password reset.')

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        messages.add_message(request, messages.WARNING, str(e))
        user = None

    if user is not None and password_reset_token.check_token(user, token):
        context = {
            'form': UserPasswordResetForm(user),
            'redirect': 'index',
            'uid': uidb64,
            'token': token
        }
        return render(request, 'password/change.html', context)
    else:
        messages.add_message(request, messages.WARNING, 'Password reset link is invalid.')
        messages.add_message(request, messages.WARNING, 'Please request a new password reset.')

    return HttpResponseRedirect('/')
