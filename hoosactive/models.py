from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Validation
from django.forms import DecimalField
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

TYPE_CHOICES = [ ['SpeedCardio','SpeedCardio'], ['DistanceCardio','DistanceCardio'], ['Bodyweight','Bodyweight'] ]

class Exercise(models.Model):
    # Exercise name
    name = models.CharField(max_length=100)
    # Exercise description
    description = models.TextField()
    # Exercise type
    type = models.CharField(max_length=100, default="", choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

class ProfileManager(models.Manager):
    def create_profile(self, us, age, hf, hi, we, bio, ci, st, ss, rn):
        profile = self.create(user=us,age=age,height_feet=hf,height_inches=hi,
                    weight_lbs=we,bio_text=bio,city=ci,state=st,show_stats=ss, receive_notifications=rn)
        return profile

STATE_CHOICES = [ ['', 'State'],
    ['AL','AL'],['AK','AK'],['AZ','AZ'],['AR','AR'],['CA','CA'],['CO','CO'],['CT','CT'],['DE','DE'],['FL','FL'],['GA','GA'],
    ['HI','HI'],['ID','ID'],['IL','IL'],['IN','IN'],['IA','IA'],['KS','KS'],['KY','KY'],['LA','LA'],['ME','ME'],['MD','MD'],
    ['MA','MA'],['MI','MI'],['MN','MN'],['MS','MS'],['MO','MO'],['MT','MT'],['NE','NE'],['NV','NV'],['NH','NH'],['NJ','NJ'],
    ['NM','NM'],['NY','NY'],['NC','NC'],['ND','ND'],['OH','OH'],['OK','OK'],['OR','OR'],['PA','PA'],['RI','RI'],['SC','SC'],
    ['SD','SD'],['TN','TN'],['TX','TX'],['UT','UT'],['VT','VT'],['VA','VA'],['WA','WA'],['WV','WV'],['WI','WI'],['WY','WY'],
]

class Profile(models.Model):
    # One-To-One Relationship with User Model
    user = models.OneToOneField(User,
        on_delete = models.CASCADE,
        primary_key = True,
    )
    # Many-To-Many Relationship with Exercise Model
    exercises = models.ManyToManyField(Exercise, blank=True)
    # Many-To-Many Relationship with other Users
    friends = models.ManyToManyField(User, related_name='friends_set', blank=True)
    # List of Users who have requested friends
    friend_requests = models.ManyToManyField(User, related_name='friend_requests_set', blank=True)
    # Age
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(4), MaxValueValidator(125)])
    # Height
    height_feet = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    height_inches = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(11)])
    # Weight
    weight_lbs = models.DecimalField(decimal_places=1,max_digits=4,validators=[MinValueValidator(0.1), MaxValueValidator(999.9)])
    # Profile Picture
    profile_pic = models.ImageField(default="default.jpg")
    # Bio
    bio_text = models.TextField(max_length=150)
    # City
    city = models.CharField(max_length=50)
    # State
    state = models.CharField(max_length=2, choices=STATE_CHOICES)

    # Toggles whether stats are shown or not
    show_stats = models.BooleanField(default=True)

    # Toggles whether friend requests are sent to their emails
    receive_notifications = models.BooleanField(default=True)

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
    def get_recent_entries(self):
        return self.user.entry_set.all().order_by('-date')[:5]
    def get_upcoming_workouts(self):
        return self.user.workout_set.filter(date__gt=timezone.now()).order_by('date')[:5]
    def update_city(self):
        for entry in self.user.entry_set.all():
            entry.city = self.city
            entry.save()
    def is_friends_with(self, user):
        return (user in self.friends.all())
    def requested_by(self, user):
        return (user in self.friend_requests.all())

class EntryManager(models.Manager):
    def create_entry(self, us, un, ci, ex, dt, cal, dur, extra):
        entry = self.create(user=us,username=un,city=ci,exercise=ex,date=dt,calories=cal,duration_hours=dur,extra=extra)
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
    # Extra data field
    extra = models.DecimalField(decimal_places=2,max_digits=4)

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
    desc = models.CharField(max_length=30, blank=True)
    # Scheduled Date
    date = models.DateTimeField(default=timezone.now, blank=True)

    objects = WorkoutManager()

    def __str__(self):
        return self.user.username + " Scheduled Exercise For " + self.date.strftime("%m/%d/%Y")
