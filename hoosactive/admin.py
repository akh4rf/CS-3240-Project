from django.contrib import admin
from .models import Profile, Exercise, Entry, Workout

# Register your models here.

admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(Entry)
admin.site.register(Workout)
