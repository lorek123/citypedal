from django.contrib import admin
from bikes.models import User, Transaction, Bike, Station, Trip, Ticket


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


class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ('id', 'created_at', 'user', 'content_type',
                    'object_id', 'is_resolved')

admin.site.register(User, UserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Bike, BikeAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Ticket, TicketAdmin)
