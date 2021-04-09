from django.http import HttpResponse
from django.shortcuts import redirect





def created_profile(view_func):
	def wrapper_func(request, *args, **kwargs):
		if(request.user.groups.exists()):
			if request.group.filter(name='profile').exists():
				return view_func(request, *args, **kwargs)
			else:
				return redirect('home')
	return wrapper_func