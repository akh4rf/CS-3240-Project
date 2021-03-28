from django.urls import path

from . import views

app_name = 'hoosactive'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('submit/', views.log_exercise, name='log_exercise'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name="register"),
    path('leaderboard/', views.leaderboard, name="leaderboard"),

]
