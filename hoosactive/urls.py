from django.urls import path

from . import views

app_name = 'hoosactive'

urlpatterns = [

    path('', views.index, name='index'),
    path('log-exercise/', views.log_exercise, name='log_exercise'),
    path('schedule-workout/', views.schedule_workout, name='schedule_workout'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name="register"),
    path('leaderboard/', views.LeaderboardView.as_view(), name="leaderboard"),
    path('leaderboard/<str:exercise_name>/<str:sort>/<str:timeframe>/', views.exercise_leaderboard, name="exercise_leaderboard")

]
