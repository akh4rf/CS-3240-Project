from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

def index(request):
    return render(request, 'hoosactive/index.html', {})

def login(request):
    return render(request, 'hoosactive/login.html', {})

def profile(request):
    return render(request, 'hoosactive/profile.html', {})
