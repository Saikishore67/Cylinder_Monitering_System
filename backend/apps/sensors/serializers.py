from rest_framework import serializers

from .models import Device, SensorReading


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device

        fields = [
            "id",
            "name",
            "device_id",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class SensorReadingSerializer(
    serializers.ModelSerializer
):
    device_name = serializers.CharField(
        source="device.name",
        read_only=True,
    )

    device_id = serializers.CharField(
        source="device.device_id",
        read_only=True,
    )

    class Meta:
        model = SensorReading

        fields = [
            "id",
            "device",
            "device_name",
            "device_id",
            "weight",
            "timestamp",
            "data",
            "received_at",
        ]

        read_only_fields = [
            "id",
            "received_at",
            "device_name",
            "device_id",
        ]


class SensorReadingCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = SensorReading

        fields = [
            "device",
            "weight",
            "timestamp",
            "data",
        ]

    def validate_weight(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Weight cannot be negative."
            )

        return value

    def validate_device(self, value):
        request = self.context["request"]

        if value.owner != request.user:
            raise serializers.ValidationError(
                "You do not own this device."
            )

        return value