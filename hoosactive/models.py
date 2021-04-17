from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Exercise(models.Model):
    # Exercise name
    name = models.CharField(max_length=100)
    # Exercise description
    description = models.TextField()

    def __str__(self):
        return self.name

class ProfileManager(models.Manager):
    def create_profile(self, us, age, hf, hi, we, bio, ci, st, ss):
        profile = self.create(user=us,age=age,height_feet=hf,height_inches=hi,
                    weight_lbs=we,bio_text=bio,city=ci,state=st,show_stats=ss)
        return profile

class Profile(models.Model):
    # One-To-One Relationship with User Model
    user = models.OneToOneField(User,
        on_delete = models.CASCADE,
        primary_key = True,
    )
    # Many-To-Many Relationship with Exercise Model
    exercises = models.ManyToManyField(Exercise, blank = True)
    # Many-To-Many Relationship with other Users
    friends = models.ManyToManyField(User, related_name='friends_set', blank = True)
    # List of Users who have requested friends
    friend_requests = models.ManyToManyField(User, related_name='friend_requests_set', blank = True)
    # Age
    age = models.PositiveSmallIntegerField()
    # Height
    height_feet = models.PositiveSmallIntegerField()
    height_inches = models.PositiveSmallIntegerField()
    # Weight
    weight_lbs = models.DecimalField(decimal_places=1,max_digits=4)
    # Profile Picture
    profile_pic = models.ImageField(default="default.jpg", null=True, blank=True)
    # Bio
    bio_text = models.TextField(max_length=150)
    # City
    city = models.CharField(max_length=50)
    # State
    state = models.CharField(max_length=2)

    # Toggles whether stats are shown or not
    show_stats = models.BooleanField(default = True)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username + "'s Profile"

    # Model Methods
    def does_exercise(self, exercise_name):
        return (self.exercises.all().filter(name = exercise_name).count() > 0)
    def add_exercise(self, exercise_name):
        # Check if relationship to exercise already exists
        if not self.does_exercise(exercise_name):
            exercise = Exercise.objects.get(name=exercise_name)
            self.exercises.add(exercise)


class EntryManager(models.Manager):
    def create_entry(self, us, un, ci, ex, dt, cal, dur):
        entry = self.create(user=us,username=un,city=ci,exercise=ex,date=dt,calories=cal,duration_hours=dur)
        if not us.profile.does_exercise(ex):
            us.profile.add_exercise(ex)
        return entry

class Entry(models.Model):
    # Foreign Key to related User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Username
    username = models.CharField(max_length=150,default="")
    # City
    city = models.CharField(max_length=100)
    # Foreign Key to related Exercise
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    # Log Date
    date = models.DateTimeField(default=timezone.now)
    # Calories Burned
    calories = models.PositiveSmallIntegerField()
    # Duration of exercise
    duration_hours = models.DecimalField(decimal_places=2,max_digits=4)

    objects = EntryManager()

    def __str__(self):
        return self.user.username + " " + self.exercise.name + " Entry " + self.date.strftime("%m/%d/%Y")

class WorkoutManager(models.Manager):
    def schedule_workout(self, us, de, dt):
        workout = self.create(user=us,desc=de,date=dt)
        return workout

class Workout(models.Model):
    # Foreign Key to related User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Short Description
    desc = models.CharField(max_length=30)
    # Scheduled Date
    date = models.DateTimeField(default=timezone.now)

    objects = WorkoutManager()

    def __str__(self):
        return self.user.username + " Scheduled Exercise For " + self.date.strftime("%m/%d/%Y")

class RunningEntry(Entry):
    # Distance Ran
    distance_miles = models.DecimalField(decimal_places=2,max_digits=5)
    # Average Speed
    average_speed = models.DecimalField(decimal_places=2,max_digits=4)

class PushUpsEntry(Entry):
    # Repetitions
    reps = models.PositiveSmallIntegerField()
