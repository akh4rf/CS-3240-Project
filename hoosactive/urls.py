from django.urls import path

from . import views


app_name = 'hoosactive'

urlpatterns = [

    path('', views.index, name='index'),
    path('log-exercise/<str:redir>/', views.log_exercise, name='log_exercise'),
    path('schedule-workout/<str:redir>/', views.schedule_workout, name='schedule_workout'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile_noname, name='profile_noname'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/create/', views.create, name='create'),
    path('profile/<str:username>/update/', views.create, name='update'),
    path('profile/<str:username>/friends/', views.friends, name='friends'),
    path('profile/<str:username>/friends/<str:error>/', views.friends_error, name='friends_error'),
    path('profile/<str:username>/send-request/<str:user2>/', views.send_request, name='send_request'),
    path('profile/<str:username>/remove-friend/<str:user2>/', views.remove_friend, name='remove_friend'),
    path('profile/<str:username>/request-respond/<str:user2>/<str:action>/', views.request_response, name='request_response'),
    path('register/', views.register, name="register"),
    path('leaderboard/', views.leaderboard, name="leaderboard"),
    path('leaderboard/<str:exercise_name>/<str:sort>/<str:timeframe>/<str:population>/', views.exercise_leaderboard, name="exercise_leaderboard"),
    path('search/', views.search, name='search'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/change/<uidb64>/<token>', views.password_change, name='password_change'),
]
