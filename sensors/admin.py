from django.contrib import admin
from .models import Hotel, CustomUser, Device, Alert


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slack_enabled', 'created_at']
    list_filter   = ['slack_enabled']
    search_fields = ['name']
    # You will create hotels here manually for now
    # Go to http://localhost:8000/admin after running createsuperuser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display  = ['uid', 'hotel', 'created_at']
    search_fields = ['uid']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'device_id', 'hotel', 'status', 'last_weight', 'last_seen_at']
    list_filter   = ['status', 'hotel']
    search_fields = ['name', 'device_id']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display  = ['device_name', 'hotel', 'type', 'severity', 'status', 'triggered_at']
    list_filter   = ['type', 'severity', 'status']
    search_fields = ['device_name']