from django.urls import path

from . import views

app_name = 'hoosactive'

urlpatterns = [

    path('', views.IndexView.as_view(), name='index'),
    path('submit/', views.log_exercise, name='log_exercise'),
    path('create/', views.create, name='create'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name="register"),
    path('leaderboard/', views.LeaderboardView.as_view(), name="leaderboard"),
    path('leaderboard/<str:exercise_name>/<str:sort>/', views.exercise_leaderboard, name="exercise_leaderboard")

]
