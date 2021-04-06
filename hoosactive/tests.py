from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from hoosactive.models import Entry, Exercise
from datetime import datetime
from django.utils import timezone
import pytz



class LoginTest(TestCase):

    # Correctly Setup User
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username='testuser')
        user.set_password('!Password1')
        user.save()

    # Test Correct Input
    def test_correct(self):
        c = Client()
        logged_in = c.login(username='testuser', password='!Password1')
        self.assertTrue(logged_in)

    # Test Correct Log Out
    def test_logout(self):
        c = Client()
        c.login(username='testuser', password='!Password1')
        User = get_user_model()
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)
        c.logout()
        self.assertFalse(user.is_anonymous)

    # Test Wrong Username
    def test_wrong_username(self):
        c = Client()
        logged_in = c.login(username='usertest', password='!Password1')
        self.assertFalse(logged_in)

    # Test Wrong Password
    def test_wrong_password(self):
        c = Client()
        logged_in = c.login(username='testuser', password='1Password!')
        self.assertFalse(logged_in)

    # Test Completely Incorrect Input
    def test_incorrect(self):
        c = Client()
        logged_in = c.login(username='usertest', password='1Password!')
        self.assertFalse(logged_in)


class RegisterTest(TestCase):

    # Test Correct Registration Input
    def test_correct_registration(self):
        c = Client()
        response = c.post('/register/', {'username': 'testuser', 'email': 'testuser@gmail.com', 'password1': '!Password1', 'password2': '!Password1'})
        logged_in = c.login(username='testuser', password='!Password1')
        self.assertTrue(logged_in)

    # Test Non-Matching Password Causing Non-Redirect
    def test_nonmatching_passwords(self):
        c = Client()
        response = c.post('/register/', {'username': 'testuser', 'email': 'testuser@gmail.com', 'password1': '!Password1', 'password2': 'wrong'})
        self.assertEquals(response.status_code, 200)

    # Test Improper Email Causing Non-Redirect
    def test_improper_email(self):
        c = Client()
        response = c.post('/register/', {'username': 'testuser', 'email': 'wrong', 'password1': '!Password1', 'password2': '!Password1'})
        self.assertEquals(response.status_code, 200)


class EntryTest(TestCase):

    def setUp(self):
        # User Setup
        User = get_user_model()
        user1 = User.objects.create(username='testuser')
        user1.set_password('!Password1')
        user1.save()
        user2 = User.objects.create(username='testuser2')
        user2.set_password('!Password1')
        user2.save()
        # Exercise Setup
        Exercise.objects.create(name="Running", description="")
        Exercise.objects.create(name="Push-Ups", description="")

    # Correctly Setup Running Entry
    def test_running_entry(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Running")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=45)
        entry = Entry.objects.get(user=user)
        entry_string = entry.user.username + " " + entry.exercise.name + " Entry " + entry.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string, "testuser Running Entry " + date.strftime("%m/%d/%Y"))

    # Correctly Setup Push-Ups Entry
    def test_pushups_entry(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Push-Ups")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=45)
        entry = Entry.objects.get(user=user)
        entry_string = entry.user.username + " " + entry.exercise.name + " Entry " + entry.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string, "testuser Push-Ups Entry " + date.strftime("%m/%d/%Y"))

    # Correctly Setup Two Entries
    def test_two_entries(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Running")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=35)
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=450, duration_hours=45)
        self.assertEquals(Entry.objects.all().count(), 2)

    # Correctly Setup Two Users
    def test_two_users(self):
        User = get_user_model()
        user1 = User.objects.get(username='testuser')
        user2 = User.objects.get(username='testuser2')
        exercise1 = Exercise.objects.get(name="Running")
        exercise2 = Exercise.objects.get(name="Push-Ups")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user1, exercise=exercise1, date=date, calories=1000, duration_hours=45)
        Entry.objects.create(user=user2, exercise=exercise2, date=date, calories=1000, duration_hours=45)
        entry1 = Entry.objects.get(user=user1)
        entry_string1 = entry1.user.username + " " + entry1.exercise.name + " Entry " + entry1.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string1, "testuser Running Entry " + date.strftime("%m/%d/%Y"))
        entry2 = Entry.objects.get(user=user2)
        entry_string2 = entry2.user.username + " " + entry2.exercise.name + " Entry " + entry2.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string2, "testuser2 Push-Ups Entry " + date.strftime("%m/%d/%Y"))


# Users with accounts deleted by admin are unable to log in.
class DeletedTest(TestCase):

    # Correctly Setup User
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username='testuser')
        user.set_password('!Password1')
        user.save()
    
    # Test Correct Input
    def test_deleted_user(self):
        c = Client()
        User = get_user_model()
        user = User.objects.get(username='testuser')
        logged_in = c.login(username='testuser', password='!Password1')
        self.assertTrue(logged_in)
        user.delete()
        logged_in = c.login(username='testuser', password='!Password1')
        self.assertFalse(logged_in)
