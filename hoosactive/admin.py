from django.contrib import admin
from .models import Profile, Exercise, Entry, Workout
from django.db.models import Count

# Register your models here.

class entryAdmin( admin.ModelAdmin ):
    list_display = ( 'user', 'city', 'exercise', 'date', 'calories', 'duration_hours', 'extra' )

class workoutAdmin( admin.ModelAdmin ):
    list_display = ( 'user', 'desc', 'date' )

class profileAdmin( admin.ModelAdmin ):
    list_display = ( 'user', 'number_of_friends', 'number_of_friend_requests', 'show_stats' )

    def number_of_friends( self, inst ):
        return inst._number_of_friends

    def number_of_friend_requests( self, inst ):
        return inst._number_of_friend_requests

    def get_queryset(self, request):
        queryset = super().get_queryset( request )
        queryset = queryset.annotate(
            _number_of_friends=Count( 'friends', distinct=True ),
            _number_of_friend_requests=Count( 'friend_requests', distinct=True )
        )
        return queryset

class exerciseAdmin( admin.ModelAdmin ):
    list_display = ( 'name', 'type', )

admin.site.register(Profile, profileAdmin)
admin.site.register(Exercise, exerciseAdmin)
admin.site.register(Entry, entryAdmin)
admin.site.register(Workout, workoutAdmin)
