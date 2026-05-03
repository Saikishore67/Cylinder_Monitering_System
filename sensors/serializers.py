from rest_framework import serializers
from .models import Hotel, CustomUser, Device, Alert


# ─────────────────────────────────────────────────────────────
# HOTEL SERIALIZER
# ─────────────────────────────────────────────────────────────

class HotelSerializer(serializers.ModelSerializer):
    """
    Returns hotel details.
    Used inside manager profile and device responses.
    """

    class Meta:
        model = Hotel
        fields = [
            'id',
            'name',
            'slack_webhook_url',
            'slack_enabled',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        # id is auto-generated
        # created_at is auto-set
        # Neither should be manually changed


class HotelBasicSerializer(serializers.ModelSerializer):
    """
    Lightweight hotel info for embedding inside other responses.
    Does not expose Slack webhook URL.
    """

    class Meta:
        model = Hotel
        fields = ['id', 'name']


# ─────────────────────────────────────────────────────────────
# MANAGER SERIALIZERS
# ─────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Creates a new manager account in Django.
    Called once after Firebase creates the account.
    Frontend sends: { uid, hotel }
    """

    class Meta:
        model = CustomUser
        fields = ['uid', 'hotel', 'fcm_token']
        # uid → comes from Firebase
        # hotel → which hotel this manager belongs to
        # fcm_token → optional push notification token

    def validate_uid(self, value):
        """
        Makes sure this Firebase UID isn't already registered.
        Prevents the same Firebase account registering twice.
        """
        if CustomUser.objects.filter(uid=value).exists():
            raise serializers.ValidationError(
                'A manager account with this Firebase UID already exists.'
            )
        # raise stops execution and returns error to frontend
        return value
        # If no error, return the value so Django can use it


class ManagerProfileSerializer(serializers.ModelSerializer):
    """
    Returns the logged-in manager's full profile.
    Used for GET /api/auth/profile/
    """

    hotel = HotelBasicSerializer(read_only=True)
    # Nested serializer — embeds hotel name inside profile
    # Instead of: "hotel": 1
    # Returns:    "hotel": { "id": 1, "name": "Grand Palace Hotel" }
    # read_only=True → can't update hotel through this serializer

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'uid',
            'hotel',
            'fcm_token',
            'created_at'
        ]
        read_only_fields = ['id', 'uid', 'created_at']
        # These should never change after registration


# ─────────────────────────────────────────────────────────────
# DEVICE SERIALIZERS
# ─────────────────────────────────────────────────────────────

class DeviceSerializer(serializers.ModelSerializer):
    """
    Full device details for the dashboard.
    Handles both listing devices (GET) and registering new ones (POST).
    """

    hotel = HotelBasicSerializer(read_only=True)
    # For GET → embeds hotel name
    # read_only → not used for input

    hotel_id = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all(),
        source='hotel',
        write_only=True
    )
    # For POST → frontend sends just the hotel id number e.g. 1
    # source='hotel' → Django maps hotel_id input to the hotel field
    # write_only=True → only accepted as input, never shown in GET
    # PrimaryKeyRelatedField → validates hotel with that id exists in DB

    class Meta:
        model = Device
        fields = [
            'id',
            'device_id',
            'hotel',
            'hotel_id',
            'name',
            'location',
            'status',
            'current_alert_type',
            'last_weight',
            'last_seen_at',
            'previous_weight',
            'previous_seen_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'current_alert_type',
            'last_weight',
            'last_seen_at',
            'previous_weight',
            'previous_seen_at',
            'created_at',
            'updated_at',
        ]
        # Manager can only set: device_id, hotel_id, name, location
        # Everything else is system-managed


# ─────────────────────────────────────────────────────────────
# WEIGHT READING SERIALIZER
# ─────────────────────────────────────────────────────────────

class WeightReadingSerializer(serializers.Serializer):
    """
    Validates incoming weight data from ESP32.

    Uses plain Serializer (not ModelSerializer) because we don't
    store weight readings as separate rows — we update the Device
    record directly. This keeps the database clean and simple.
    """

    device_id = serializers.CharField()
    # Hardware ID of the ESP32 sending data
    # e.g. "ESP32-A1B2C3D4"

    weight_kg = serializers.FloatField()
    # Current weight reading from the load cell in kg

    def validate_weight_kg(self, value):
        """
        Field-level validation for weight_kg.
        Django automatically calls validate_<fieldname>() methods.
        Runs after the field type is confirmed to be a float.
        """

        if value < 0:
            raise serializers.ValidationError(
                'Weight cannot be negative. Check load cell calibration.'
            )
        # Load cells can give negative readings when miscalibrated

        if value > 100:
            raise serializers.ValidationError(
                'Weight above 100kg is not valid. Possible sensor error.'
            )
        # No gas cylinder weighs over 100kg — must be a sensor fault

        return value

    def validate_device_id(self, value):
        """
        Confirms this device_id exists in the database.
        Rejects data from unknown or unregistered ESP32 devices.
        """

        if not Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError(
                f'Device "{value}" is not registered in the system.'
            )
        return value


# ─────────────────────────────────────────────────────────────
# ALERT SERIALIZERS
# ─────────────────────────────────────────────────────────────

class AlertSerializer(serializers.ModelSerializer):
    """
    Full alert details for the dashboard.
    """

    hotel = HotelBasicSerializer(read_only=True)
    # Embeds hotel name inside each alert

    class Meta:
        model = Alert
        fields = [
            'id',
            'device',
            'device_name',
            'hotel',
            'type',
            'severity',
            'status',
            'triggered_at',
            'resolved_at',
            'last_notified_at',
        ]
        read_only_fields = [
            'id',
            'device_name',
            'triggered_at',
            'last_notified_at',
        ]


class AlertResolveSerializer(serializers.ModelSerializer):
    """
    Used when manager marks an alert as resolved.
    Only allows updating status and resolved_at.
    Manager cannot change type, severity, or device.
    """

    class Meta:
        model = Alert
        fields = ['status', 'resolved_at']

    def validate_status(self, value):
        """Ensures manager can only set status to resolved."""
        if value != 'resolved':
            raise serializers.ValidationError(
                'You can only set status to resolved.'
            )
        return value