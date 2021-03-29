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



class Profile(models.Model):
    # One-To-One Relationship with User Model
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        primary_key = True,
    )
    # Many-To-Many Relationship with Exercise Model
    exercises = models.ManyToManyField(Exercise)
    # Age
    age = models.PositiveSmallIntegerField()
    # Height
    height_feet = models.PositiveSmallIntegerField()
    height_inches = models.PositiveSmallIntegerField()
    # Weight
    weight_lbs = models.DecimalField(decimal_places=1,max_digits=4)
    # Profile Picture
    #profile_picture = models.ImageField()
    # Bio
    bio_text = models.TextField()
    # City
    city = models.CharField(max_length=100)
    # State
    state = models.CharField(max_length=2)

    # Toggles whether stats are shown or not
    show_stats = models.BooleanField(default = True)

    def __str__(self):
        return self.user.username + "'s Profile"

    # Model Methods
    def does_exercise(self, exercise_name):
        return (self.exercises.all().filter(name = exercise_name).count() > 0)
    def add_exercise(self, exercise_name):
        # Check if relationship to exercise already exists
        if (self.does_exercise(exercise_name)):
            exercise = Exercise.objects.filter(name = exercise_name)
            self.exercises.add(exercise)


class EntryManager(models.Manager):
    def create_entry(self, us, ex, dt, cal, dur):
        entry = self.create(user=us,exercise=ex,date=dt,calories=cal,duration_hours=dur)
        return entry

class Entry(models.Model):
    # Foreign Key to related User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Foreign Key to related Exercise
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    # Log Date
    date = models.DateTimeField(default=datetime.now())
    # Calories Burned
    calories = models.PositiveSmallIntegerField()
    # Duration of exercise
    duration_hours = models.DecimalField(decimal_places=2,max_digits=4)

    objects = EntryManager()

    def __str__(self):
        return self.user.username + " " + self.exercise.name + " Entry " + self.date.strftime("%m/%d/%Y")



class RunningEntry(Entry):
    # Distance Ran
    distance_miles = models.DecimalField(decimal_places=2,max_digits=5)
    # Average Speed
    average_speed = models.DecimalField(decimal_places=2,max_digits=4)

class PushUpsEntry(Entry):
    # Repetitions
    reps = models.PositiveSmallIntegerField()
