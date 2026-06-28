from rest_framework import serializers


class DeviceSerializer(serializers.Serializer):
    name = serializers.CharField()
    device_id = serializers.CharField()


class SensorReadingCreateSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    weight = serializers.FloatField()
    timestamp = serializers.DateTimeField(required=False)
    data = serializers.DictField(required=False, default=dict)

    def validate_weight(self, value):
        if value < 0:
            raise serializers.ValidationError("Weight cannot be negative.")
        return value


class SensorReadingSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    device_id = serializers.CharField()
    weight = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    data = serializers.DictField(required=False, default=dict)
    received_at = serializers.DateTimeField(read_only=True)