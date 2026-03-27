from django.contrib import admin
from .models import CustomUser, BusLocation, TripLog, Feedback, SpeedAlert


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'role', 'email', 'date_joined')
    list_filter = ('role',)
    search_fields = ('username', 'full_name', 'email')


@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'lat', 'lng', 'speed', 'occupancy', 'timestamp')
    list_filter = ('device_id',)


@admin.register(TripLog)
class TripLogAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'route_name', 'departure_time', 'arrival_time')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('bus_id', 'user', 'rating', 'submitted_at')
    list_filter = ('rating', 'bus_id')


@admin.register(SpeedAlert)
class SpeedAlertAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'speed', 'triggered_at', 'acknowledged')
    list_filter = ('acknowledged', 'device_id')
    actions = ['mark_acknowledged']

    def mark_acknowledged(self, request, queryset):
        queryset.update(acknowledged=True)
    mark_acknowledged.short_description = 'Mark selected alerts as acknowledged'
