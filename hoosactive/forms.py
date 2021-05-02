from django.forms import ModelForm
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django import forms
from hoosactive.models import Profile

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['age', 'height_feet', 'height_inches', 'weight_lbs', 'bio_text', 'city', 'state', 'show_stats', 'receive_notifications']

class ChangePictureForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['profile_pic']

class UserPasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Password',
        help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'password',
            'type': 'password',
            'id': 'user_password',
        }))

    new_password2 = forms.CharField(label='Confirm password',
        help_text=False,
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'confirm password',
            'type': 'password',
            'id': 'user_password',
        }))


class UserForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(label='Email address',
        max_length=254,
        required=True,
        widget=forms.TextInput(
         attrs={'class': 'form-control',
                'placeholder': 'email address',
                'type': 'text',
                'id': 'email_address'
                }
        ))

