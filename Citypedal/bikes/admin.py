from django.contrib import admin
from bikes.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'joined_at', 'first_name', 'last_name',
                    'is_active', 'level', 'balance')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'trip', 'type')


class BikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'state')


class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'is_active')


class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_station', 'to_station', 'user', 'bike',
                    'started_at', 'ended_at')


admin.site.register(User, UserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Bike, BikeAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Trip, TripAdmin)