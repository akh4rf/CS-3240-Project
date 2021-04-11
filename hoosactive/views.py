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
from .decorators import created_profile

class IndexView(generic.TemplateView):
    template_name = 'hoosactive/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['exercise_list'] = Exercise.objects.order_by('name')
        return context

def log_exercise(request):
    user = request.user
    if request.method == 'POST':
        exer = Exercise.objects.get(name=request.POST['drop'])
        entry = Entry.objects.create_entry(user,exer,request.POST['date'],request.POST['calories_burned'],request.POST['duration'])
        return redirect('hoosactive:index')

def register(request):
    if request.user.is_authenticated:
        return redirect('hoosactive:index.html')
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
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if request.user.groups.filter(name='profile').exists():
                    return redirect('hoosactive:index')
                else:
                    return redirect('hoosactive:create')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'hoosactive/login.html', context)


def profile(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='profile').exists():
            return render(request, 'hoosactive/profile.html', {})
        else:
            return redirect('hoosactive:create')
    else:
        return redirect('hoosactive:login')


def create(request):
    if request.user.is_authenticated:
        form = PostForm()
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                #age = form.cleaned_data.get('age')
                #messages.success(request, 'Profile was created for ' + age)
                group, created = Group.objects.get_or_create(name='profile')

                request.user.groups.add(group)
                return redirect('hoosactive:profile')

        context = {'form': form}
        return render(request, 'hoosactive/create.html', context)
    else:
        return redirect('hoosactive:login')
class LeaderboardView(generic.TemplateView):
    template_name = 'hoosactive/leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        context['exercise_list'] = Exercise.objects.order_by('name')
        return context

def exercise_leaderboard(request, exercise_name, sort):
    exercise = get_object_or_404(Exercise, name=exercise_name)
    # d = date.today()
    # if (timeframe = day):
    #   set = exercise.entry_set.filter(date__day=d)
    # elif (timeframe = week):
    #   week_ago = d - timedelta(days=6)
    #   set = exercise.entry_set.filter(date__gt=week_ago)
    # elif (timeframe = month):
    #   set = exercise.entry_set.filter(date__month=d.month)

    entry_list = exercise.entry_set.order_by('-'+sort)
    return render(request, 'hoosactive/leaderboard.html', {
        'exercise_list': Exercise.objects.order_by('name'),
        'exercise': exercise,
        'entry_list': entry_list
    })
