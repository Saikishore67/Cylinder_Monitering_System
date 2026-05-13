from django.contrib import admin

from .models import Device, SensorReading


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "device_id",
        "owner",
        "created_at",
    )

    search_fields = (
        "name",
        "device_id",
        "owner__email",
    )

    list_filter = (
        "created_at",
    )


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "weight",
        "timestamp",
        "received_at",
    )

    search_fields = (
        "device__name",
        "device__device_id",
    )

    list_filter = (
        "timestamp",
        "received_at",
    )