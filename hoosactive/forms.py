from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
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
		fields = ['age', 'height_feet', 'height_inches', 'weight_lbs', 'bio_text', 'city', 'state', 'show_stats']