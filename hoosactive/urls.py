from django.urls import path

from . import views

app_name = 'hoosactive'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name="register"),
]
