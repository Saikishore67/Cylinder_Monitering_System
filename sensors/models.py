from django.db import models


# ─────────────────────────────────────────────────────────────
# HOTEL
# Represents one hotel or food business using the system
# Created manually via Django admin for now
# ─────────────────────────────────────────────────────────────

class Hotel(models.Model):

    name = models.CharField(max_length=200)
    # Hotel name — e.g. "Grand Palace Hotel"

    slack_webhook_url = models.URLField(blank=True, null=True)
    # Slack webhook URL for sending alerts
    # Optional — manager can add this later from settings

    slack_enabled = models.BooleanField(default=False)
    # Whether Slack notifications are active
    # Starts as False

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ─────────────────────────────────────────────────────────────
# MANAGER (CustomUser)
# One manager per hotel
# Firebase handles their login — Django stores their data
# No roles needed at this stage
# ─────────────────────────────────────────────────────────────

class CustomUser(models.Model):

    uid = models.CharField(max_length=128, unique=True)
    # Firebase UID — the link between Firebase and Django
    # e.g. "uid_xK9mP2qL..."
    # unique=True → one Django record per Firebase account

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    # Which hotel this manager belongs to
    # SET_NULL → if hotel deleted, manager still exists
    # null=True → required for SET_NULL
    # blank=True → allowed to be empty in forms

    fcm_token = models.CharField(max_length=500, blank=True, null=True)
    # Firebase Cloud Messaging token
    # Used for push notifications later — optional for now

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Manager ({self.uid})"

    class Meta:
        ordering = ['created_at']


# ─────────────────────────────────────────────────────────────
# DEVICE
# One ESP32 + load cell monitoring one gas cylinder
# Belongs to a hotel
# ─────────────────────────────────────────────────────────────

class Device(models.Model):

    class Status(models.TextChoices):
        NORMAL  = 'normal',  'Normal'
        LOW     = 'low',     'Low'
        EMPTY   = 'empty',   'Empty'
        OFFLINE = 'offline', 'Offline'
    # TextChoices restricts this field to only these four values
    # Prevents invalid values being stored

    class AlertType(models.TextChoices):
        LOW     = 'low',     'Low'
        EMPTY   = 'empty',   'Empty'
        OFFLINE = 'offline', 'Offline'

    device_id = models.CharField(max_length=100, unique=True)
    # Hardware ID of the ESP32
    # e.g. "ESP32-A1B2C3D4"
    # unique=True → no two devices share the same ID

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    # Which hotel this device belongs to
    # CASCADE → if hotel deleted, all its devices deleted too

    name = models.CharField(max_length=200)
    # Human-readable label — e.g. "Main Kitchen Cylinder 1"

    location = models.CharField(max_length=200)
    # Physical location — e.g. "Ground Floor Kitchen"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NORMAL
    )
    # Updated automatically when ESP32 sends data

    current_alert_type = models.CharField(
        max_length=10,
        choices=AlertType.choices,
        null=True,
        blank=True
    )
    # NULL means no active alert
    # Set automatically by the system

    last_weight = models.FloatField(null=True, blank=True)
    # Most recent weight reading in kg
    # Null when device is first registered

    last_seen_at = models.DateTimeField(null=True, blank=True)
    # Last time this device sent data
    # Used to detect when a device goes OFFLINE

    previous_weight = models.FloatField(null=True, blank=True)
    # Reading before the latest one
    # Used to calculate gas consumption rate

    previous_seen_at = models.DateTimeField(null=True, blank=True)
    # Timestamp of the previous reading

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    # auto_now=True → updates every time this record is saved
    # Different from auto_now_add which only sets once on creation

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    class Meta:
        ordering = ['hotel', 'name']


# ─────────────────────────────────────────────────────────────
# ALERT
# Created when a device hits a low/empty/offline threshold
# One device can create many alerts over its lifetime
# ─────────────────────────────────────────────────────────────

class Alert(models.Model):

    class AlertType(models.TextChoices):
        LOW     = 'low',     'Low'
        EMPTY   = 'empty',   'Empty'
        OFFLINE = 'offline', 'Offline'

    class Severity(models.TextChoices):
        WARNING  = 'warning',  'Warning'
        CRITICAL = 'critical', 'Critical'

    class AlertStatus(models.TextChoices):
        ACTIVE   = 'active',   'Active'
        RESOLVED = 'resolved', 'Resolved'

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    # Which device triggered this alert

    device_name = models.CharField(max_length=200)
    # Stored separately so historical alerts keep the original name
    # Even if device is renamed later

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    # Stored directly for efficient querying
    # Avoids joining through Device every time

    type = models.CharField(max_length=10, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)

    status = models.CharField(
        max_length=10,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE
    )
    # Starts as active
    # Manager sets to resolved when cylinder is refilled

    triggered_at = models.DateTimeField(auto_now_add=True)
    # Auto-set when alert is created

    resolved_at = models.DateTimeField(null=True, blank=True)
    # Null until manager resolves it

    last_notified_at = models.DateTimeField(null=True, blank=True)
    # Last time Slack notification was sent
    # Prevents repeated spam notifications

    def __str__(self):
        return f"{self.device_name} - {self.type} ({self.status})"

    class Meta:
        ordering = ['-triggered_at']
        # Most recent alerts first
        # '-' means descending order