from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from hoosactive.models import Entry, Exercise, Workout, Profile
from hoosactive.models import Entry, Exercise
from datetime import datetime, timedelta
from django.urls import reverse
from django.core import mail
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

    # Test Login without activation
    def test_correct_registration(self):
        c = Client(HTTP_HOST='example.com')
        response = c.post('/register/', {'username': 'testuser', 'email': 'testuser@gmail.com', 'password1': '!Password1', 'password2': '!Password1'}, secure=True)
        logged_in = c.login(username='testuser', password='!Password1')
        self.assertFalse(logged_in)

    # Test Non-Matching Password Causing Non-Redirect
    def test_nonmatching_passwords(self):
        c = Client()
        response = c.post('/register/', {'username': 'testuser', 'email': 'testuser@gmail.com', 'password1': '!Password1', 'password2': 'wrong'}, secure=True)
        self.assertEquals(response.status_code, 200)

    # Test Improper Email Causing Non-Redirect
    def test_improper_email(self):
        c = Client()
        response = c.post('/register/', {'username': 'testuser', 'email': 'wrong', 'password1': '!Password1', 'password2': '!Password1'}, secure=True)
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
        Exercise.objects.create(name="Speed Running", description="", type="SpeedCardio")
        Exercise.objects.create(name="Push-Ups", description="", type="Bodyweight")

    # Correctly Setup Running Entry
    def test_running_entry(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Speed Running")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=45, extra=20)
        entry = Entry.objects.get(user=user)
        entry_string = entry.user.username + " " + entry.exercise.name + " Entry " + entry.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string, "testuser Speed Running Entry " + date.strftime("%m/%d/%Y"))

    # Correctly Setup Push-Ups Entry
    def test_pushups_entry(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Push-Ups")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=45, extra=20)
        entry = Entry.objects.get(user=user)
        entry_string = entry.user.username + " " + entry.exercise.name + " Entry " + entry.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string, "testuser Push-Ups Entry " + date.strftime("%m/%d/%Y"))

    # Correctly Setup Two Entries
    def test_two_entries(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Speed Running")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=35, extra=20)
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=450, duration_hours=45, extra=30)
        self.assertEquals(Entry.objects.all().count(), 2)

    # Correctly Setup Two Users
    def test_two_users(self):
        User = get_user_model()
        user1 = User.objects.get(username='testuser')
        user2 = User.objects.get(username='testuser2')
        exercise1 = Exercise.objects.get(name="Speed Running")
        exercise2 = Exercise.objects.get(name="Push-Ups")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user1, exercise=exercise1, date=date, calories=1000, duration_hours=45, extra=20)
        Entry.objects.create(user=user2, exercise=exercise2, date=date, calories=1000, duration_hours=45, extra=20)
        entry1 = Entry.objects.get(user=user1)
        entry_string1 = entry1.user.username + " " + entry1.exercise.name + " Entry " + entry1.date.strftime("%m/%d/%Y")
        self.assertEquals(entry_string1, "testuser Speed Running Entry " + date.strftime("%m/%d/%Y"))
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


# Test if the Entered Fitness data is correctly counted in the cumulative "score"
class LeaderboardTest(TestCase):

    # Correctly Setup User
    def setUp(self):
        # User Setup
        User = get_user_model()
        user1 = User.objects.create(username='testuser')
        user1.set_password('!Password1')
        user1.save()
        user2 = User.objects.create(username='testuser2')
        user2.set_password('!Password1')
        user2.save()
        user3 = User.objects.create(username='testuser3')
        user3.set_password('!Password1')
        user3.save()
        user4 = User.objects.create(username='testuser4')
        user4.set_password('!Password1')
        user4.save()
        # Exercise Setup
        Exercise.objects.create(name="Speed Running", description="", type="SpeedCardio")
        Exercise.objects.create(name="Push-Ups", description="", type="Bodyweight")

    # Test if leaderboard request is handled correctly for signed in user
    def test_leaderboard_response(self):
        c = Client()
        c.login( username = 'testuser', password = '!Password1' )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard', args=[
            "Speed Running", "calories", "week", "all" ] ), secure=True )
        self.assertEquals( response.status_code, 200 )


    # Test to see if the score is posted to leaderboard
    def test_correct_score(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Speed Running")
        date = pytz.utc.localize(datetime.now())
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=1000, duration_hours=35, extra=20)
        Entry.objects.create(user=user, exercise=exercise, date=date, calories=450, duration_hours=45, extra=30)

        c = Client()
        c.login( username = 'testuser', password = '!Password1' )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard', args=[
            "Speed Running", "calories", "week", "all" ] ), secure=True )
        entry_list = response.context['entry_list']
        self.assertEquals( entry_list[0]['total_cals'], 1450 )


    # Test to see if the scores are correctly sorted by date
    def test_sorting_date(self):
        User = get_user_model()
        user = User.objects.get(username='testuser')
        exercise = Exercise.objects.get(name="Speed Running")
        date1 = pytz.utc.localize(datetime.now())
        date2 = date1 - timedelta( days = 6 )
        date3 = date1 - timedelta( days = 20 )
        Entry.objects.create(user=user, exercise=exercise, date=date1, calories=1000, duration_hours=35, extra=50)
        Entry.objects.create(user=user, exercise=exercise, date=date2, calories=450, duration_hours=45, extra=40)
        Entry.objects.create(user=user, exercise=exercise, date=date3, calories=600, duration_hours=40, extra=30)

        c = Client()
        c.login( username = 'testuser', password = '!Password1' )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard', args=[
            "Speed Running", "calories", "month", "all" ] ), secure=True )
        entry_list_month = response.context['entry_list']
        self.assertEquals( entry_list_month[0]['total_cals'], 2050 )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard', args=[
            "Speed Running", "calories", "week", "all" ] ), secure=True )
        entry_list_week = response.context['entry_list']
        self.assertEquals( entry_list_week[0]['total_cals'], 1450 )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard', args=[
            "Speed Running", "calories", "day", "all" ] ), secure=True )
        entry_list_week = response.context['entry_list']
        self.assertEquals( entry_list_week[0]['total_cals'], 1000 )


    # Test to see if scores are in the correct order and sorted properly
    def test_correct_order_two(self):
        User = get_user_model()
        user1 = User.objects.get( username = 'testuser' )
        user2 = User.objects.get( username = 'testuser2' )

        exercise = Exercise.objects.get( name = "Speed Running" )
        date = pytz.utc.localize( datetime.now() )
        Entry.objects.create( user=user1, username=user1.username,
                             city="Tacoma", exercise=exercise, date=date,
                             calories=1000, duration_hours=35, extra=50 )
        Entry.objects.create( user=user2, username=user2.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=500, duration_hours=50, extra=50 )

        c = Client()

        # Sort by calories
        c.login( username = 'testuser', password = "!Password1" )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "all"] ), secure=True )
        entry_list = response.context['entry_list']
        self.assertTrue( entry_list[0]['username'] == "testuser" )
        self.assertTrue( entry_list[1]['username'] == "testuser2" )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "duration_hours", "week", "all"] ), secure=True )
        # Sort by hours
        entry_list_hours = response.context['entry_list']
        self.assertTrue( entry_list_hours[0]['username'] == "testuser2" )
        self.assertTrue( entry_list_hours[1]['username'] == "testuser" )

    # Test to see if scores are correctly sorted with friends
    def test_correct_order_friends_running(self):
        User = get_user_model()
        user1 = User.objects.get( username = 'testuser' )
        Profile.objects.create_profile( us=user1, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user2 = User.objects.get( username = 'testuser2' )
        Profile.objects.create_profile( us=user2, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )

        exercise = Exercise.objects.get( name = "Speed Running" )
        date = pytz.utc.localize( datetime.now() )
        Entry.objects.create( user=user1, username=user1.username,
                             city="Tacoma", exercise=exercise, date=date,
                             calories=1000, duration_hours=35, extra=50 )
        Entry.objects.create( user=user2, username=user2.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=500, duration_hours=50, extra=50 )

        c = Client()

        # Sort by calories
        c.login( username = 'testuser', password = "!Password1" )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "all"] ), secure=True )
        entry_list = response.context['entry_list']
        self.assertEqual( len(entry_list), 2 )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "friends"] ), secure=True )
        # Sort by hours
        entry_list = response.context['entry_list']
        self.assertEqual( len(entry_list), 1 )

    def test_correct_order_friends_pushups(self):
        User = get_user_model()
        user1 = User.objects.get( username = 'testuser' )
        Profile.objects.create_profile( us=user1, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user2 = User.objects.get( username = 'testuser2' )
        Profile.objects.create_profile( us=user2, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )

        exercise = Exercise.objects.get( name = "Speed Running" )
        date = pytz.utc.localize( datetime.now() )
        Entry.objects.create( user=user1, username=user1.username,
                             city="Tacoma", exercise=exercise, date=date,
                             calories=1000, duration_hours=35, extra=30 )
        Entry.objects.create( user=user2, username=user2.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=500, duration_hours=50, extra=30 )

        c = Client()

        # Sort by calories
        c.login( username = 'testuser', password = "!Password1" )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "all"] ), secure=True )
        entry_list = response.context['entry_list']
        self.assertEqual( len(entry_list), 2 )
        self.assertEqual( entry_list[0]['username'], "testuser" )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "friends"] ), secure=True )
        # Sort by hours
        entry_list = response.context['entry_list']
        self.assertEqual( len(entry_list), 1)
        self.assertEqual( entry_list[0]['username'], "testuser" )

    # Test to see if scores are in the correct order and sorted properly
    def test_correct_order_many(self):
        User = get_user_model()
        user1 = User.objects.get( username = 'testuser' )
        user2 = User.objects.get( username = 'testuser2' )
        user3 = User.objects.get( username = 'testuser3' )
        user4 = User.objects.get( username = 'testuser4' )

        exercise = Exercise.objects.get( name = "Speed Running" )
        date = pytz.utc.localize( datetime.now() )
        Entry.objects.create( user=user1, username=user1.username,
                             city="Tacoma", exercise=exercise, date=date,
                             calories=1000, duration_hours=35, extra=50 )
        Entry.objects.create( user=user2, username=user2.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=500, duration_hours=50, extra=40 )
        Entry.objects.create( user=user3, username=user3.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=1500, duration_hours=60, extra=30 )
        Entry.objects.create( user=user4, username=user4.username,
                             city="Charlottesville", exercise=exercise,
                             date=date, calories=200, duration_hours=20, extra=10 )

        c = Client()

        # Sort by calories
        c.login( username = 'testuser', password = "!Password1" )
        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "calories", "week", "all"] ), secure=True )
        entry_list = response.context['entry_list']
        self.assertTrue( entry_list[0]['username'] == "testuser3" )
        self.assertTrue( entry_list[1]['username'] == "testuser" )
        self.assertTrue( entry_list[2]['username'] == "testuser2" )
        self.assertTrue( entry_list[3]['username'] == "testuser4" )

        response = c.get( reverse( 'hoosactive:exercise_leaderboard',
                                  args=["Speed Running", "duration_hours", "week", "all"] ), secure=True )
        # Sort by hours
        entry_list_hours = response.context['entry_list']
        self.assertTrue( entry_list_hours[0]['username'] == "testuser3" )
        self.assertTrue( entry_list_hours[1]['username'] == "testuser2" )
        self.assertTrue( entry_list_hours[2]['username'] == "testuser" )
        self.assertTrue( entry_list_hours[3]['username'] == "testuser4" )

class WorkoutScheduleTest(TestCase):
    # Setup
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username='testuser')
        user.set_password('!Password1')
        user.save()

    # Test simple workout entry
    def test_workout_creation(self):
        User = get_user_model()
        user = User.objects.get( username="testuser" )
        date = datetime( year=2021, month=5, day=1, hour=9, minute=0,
                                 tzinfo=pytz.UTC)
        Workout.objects.create( user=user, desc="1-mile run", date=date )
        workout = Workout.objects.get( user=user )
        workout_string = workout.user.username + " Scheduled Exercise for " + workout.date.strftime("%m/%d/%Y")
        self.assertEquals( workout_string, "testuser Scheduled Exercise for 05/01/2021" )


    # Test multiple entries
    def test_workout_creation_multiple(self):
        User = get_user_model()
        user = User.objects.get( username="testuser" )
        date1 = datetime( year=2021, month=5, day=1, hour=9, minute=0,
                                 tzinfo=pytz.UTC)
        date2 = datetime( year=2021, month=5, day=2, hour=9, minute=0,
                                 tzinfo=pytz.UTC)
        Workout.objects.create( user=user, desc="1-mile run", date=date1 )
        Workout.objects.create( user=user, desc="2-mile run", date=date2 )
        workout1 = Workout.objects.get( date=date1 )
        workout2 = Workout.objects.get( date=date2 )
        workout_string1 = workout1.user.username + " Scheduled Exercise for " + workout1.date.strftime("%m/%d/%Y")
        workout_string2 = workout2.user.username + " Scheduled Exercise for " + workout2.date.strftime("%m/%d/%Y")
        self.assertEquals( workout_string1, "testuser Scheduled Exercise for 05/01/2021" )
        self.assertEquals( workout_string2, "testuser Scheduled Exercise for 05/02/2021" )


class FriendRequestTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username='testuser')
        user.set_password('!Password1')
        user.save()
        user2 = User.objects.create(username='testuser2')
        user2.set_password('!Password1')
        user2.save()
        user3 = User.objects.create(username='testuser3')
        user3.set_password('!Password1')
        user3.save()
        user4 = User.objects.create(username='testuser4')
        user4.set_password('!Password1')
        user4.save()

    def test_not_friends(self):
        User = get_user_model()
        user = User.objects.get( username='testuser' )
        Profile.objects.create_profile( us=user, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user2 = User.objects.get( username='testuser2' )
        Profile.objects.create_profile( us=user2, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )

        self.assertFalse( user.profile.is_friends_with(user2) )

    def test_friend_add(self):
        User = get_user_model()
        user = User.objects.get( username='testuser' )
        Profile.objects.create_profile( us=user, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user2 = User.objects.get( username='testuser2' )
        Profile.objects.create_profile( us=user2, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )

        user.profile.friends.add(user2)
        user2.profile.friends.add(user)

        self.assertEqual( user.profile.friends.all()[0], user2 )
        self.assertEqual( user2.profile.friends.all()[0], user )

    def test_freind_add_many(self):
        User = get_user_model()
        user = User.objects.get( username='testuser' )
        Profile.objects.create_profile( us=user, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user2 = User.objects.get( username='testuser2' )
        Profile.objects.create_profile( us=user2, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user3 = User.objects.get( username='testuser3' )
        Profile.objects.create_profile( us=user3, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )
        user4 = User.objects.get( username='testuser4' )
        Profile.objects.create_profile( us=user4, age=23,hf=6, hi=4, we=185, ci='Tacoma',
                                       st='WA', ss=True, rn=False, bio="Stuff" )

        user.profile.friends.add(user2)
        user.profile.friends.add(user3)
        user.profile.friends.add(user4)
        self.assertEqual( user.profile.friends.all()[0], user2 )
        self.assertEqual( user.profile.friends.all()[1], user3 )
        self.assertEqual( user.profile.friends.all()[2], user4 )
