from django.urls import path

from . import views


app_name = 'hoosactive'

urlpatterns = [

    path('', views.index, name='index'),
    path('log-exercise/<str:redir>/', views.log_exercise, name='log_exercise'),
    path('schedule-workout/<str:redir>/', views.schedule_workout, name='schedule_workout'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile_noname, name='profile_noname'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('profile/<str:username>/create/', views.create, name='create'),
    path('profile/<str:username>/update/', views.create, name='update'),
    path('register/', views.register, name="register"),
    path('leaderboard/', views.leaderboard, name="leaderboard"),
    path('leaderboard/<str:exercise_name>/<str:sort>/<str:timeframe>/', views.exercise_leaderboard, name="exercise_leaderboard"),
    path('profile/<str:username>/friends/', views.friends, name='friends'),
    path('search/', views.search, name='search')
]
