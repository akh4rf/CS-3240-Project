from django.test import TestCase, Client
from django.contrib.auth import get_user_model


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