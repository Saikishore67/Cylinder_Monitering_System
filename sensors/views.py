from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
 
from .models import Hotel, Device, Alert
from .serializers import (
    RegisterSerializer,
    ManagerProfileSerializer,
    DeviceSerializer,
    WeightReadingSerializer,
    AlertSerializer,
    AlertResolveSerializer,
)
 
# ── Gas level thresholds ──────────────────────────────────────
LOW_THRESHOLD   = 30   # Below 30% → LOW alert
EMPTY_THRESHOLD = 10   # Below 10% → EMPTY alert
 
 
# ─────────────────────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────────────────────
 
class RegisterView(APIView):
    """
    POST /api/auth/register/
 
    Called ONCE after Firebase creates the manager's account.
    Saves the Firebase UID + hotel info into Django's database.
 
    No token required — manager has a Firebase account
    but no Django record yet at this point.
    """
 
    permission_classes = [AllowAny]
    # AllowAny → no Firebase token required for this endpoint
    # If we required auth here, new managers could never register
 
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        # request.data → the JSON body sent by frontend
        # Example: { "uid": "firebaseUID123", "hotel": 1 }
 
        if serializer.is_valid():
            user = serializer.save()
            # Saves new CustomUser to PostgreSQL
 
            return Response(
                {
                    'message': 'Manager account registered successfully.',
                    'id': user.id,
                    'uid': user.uid,
                },
                status=status.HTTP_201_CREATED
            )
            # 201 Created → standard HTTP response for resource creation
 
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        # 400 Bad Request → validation failed
        # Returns exactly what went wrong so frontend can show it
 
 
class ManagerProfileView(APIView):
    """
    GET /api/auth/profile/
 
    Returns the logged-in manager's profile.
    Firebase token required in Authorization header.
    """
 
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        serializer = ManagerProfileSerializer(request.user)
        # request.user is set automatically by FirebaseAuthentication
        # No manual lookup needed — Django handles it
 
        return Response(serializer.data, status=status.HTTP_200_OK)
 
 
# ─────────────────────────────────────────────────────────────
# DEVICE VIEWS
# ─────────────────────────────────────────────────────────────
 
class DeviceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/devices/ → list all devices for this manager's hotel
    POST /api/devices/ → register a new ESP32 device
    """
 
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
 
    def get_queryset(self):
        return Device.objects.filter(hotel=self.request.user.hotel)
        # filter() → only return devices belonging to this manager's hotel
        # self.request.user → the logged-in manager (set by FirebaseAuthentication)
        # self.request.user.hotel → their linked hotel
        # Managers never see other hotels' devices
 
    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.hotel)
        # perform_create() runs when POST is successful
        # Automatically sets hotel to the manager's hotel
        # Manager doesn't need to send hotel_id in POST body
        # The system knows which hotel they belong to
 
 
class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/devices/<id>/ → view one device
    PATCH  /api/devices/<id>/ → update device name or location
    DELETE /api/devices/<id>/ → remove a device
    """
 
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
 
    def get_queryset(self):
        return Device.objects.filter(hotel=self.request.user.hotel)
        # Manager can only access their own hotel's devices
        # If they try to access another hotel's device ID,
        # Django returns 404 — not 403 — which doesn't reveal it exists
 
 
# ─────────────────────────────────────────────────────────────
# WEIGHT READING VIEW
# This is the most important endpoint — ESP32 sends data here
# ─────────────────────────────────────────────────────────────
 
class WeightReadingView(APIView):
    """
    POST /api/readings/
 
    Called by ESP32 every time it measures cylinder weight.
 
    Step by step what happens:
    1. Validate incoming data (device exists, weight is valid)
    2. Save previous reading before overwriting
    3. Update device with new weight and timestamp
    4. Calculate gas percentage remaining
    5. Determine status: normal / low / empty
    6. Create alert if gas is low or empty
    7. Send Slack notification if hotel has it enabled
    8. Return response to ESP32
    """
 
    permission_classes = [AllowAny]
    # ESP32 devices don't have Firebase accounts
    # They identify themselves via device_id
    # The serializer validates device_id exists in DB
 
    def post(self, request):
 
        # ── Step 1: Validate incoming data ──────────────────
        serializer = WeightReadingSerializer(data=request.data)
        # request.data → JSON body from ESP32
        # Example: { "device_id": "ESP32-A1B2", "weight_kg": 4.2 }
 
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        # If device_id doesn't exist or weight is invalid → stop here
 
        device_id = serializer.validated_data['device_id']
        weight_kg = serializer.validated_data['weight_kg']
        # validated_data → cleaned and verified values
        # Safe to use without any extra checks
 
        device = Device.objects.get(device_id=device_id)
        # We know this exists — serializer already confirmed it
        # .get() fetches the single matching row from PostgreSQL
 
        # ── Step 2: Save previous reading ───────────────────
        device.previous_weight   = device.last_weight
        device.previous_seen_at  = device.last_seen_at
        # Shift current reading into "previous" slot
        # Before we overwrite it with the new reading
        # This lets us calculate consumption rate later
 
        # ── Step 3: Update with new reading ─────────────────
        device.last_weight  = weight_kg
        device.last_seen_at = timezone.now()
        # timezone.now() → current time in IST (set in settings.py)
 
        # ── Step 4: Calculate gas percentage ────────────────
        capacity_kg = 14.2
        # Standard commercial cylinder capacity
        # TODO: Make this a field on Device model later
        # So different cylinder sizes are supported
 
        percentage = (weight_kg / capacity_kg) * 100
        # Example: 4.2kg / 14.2kg * 100 = 29.6%
        # This tells us how full the cylinder is
 
        # ── Step 5: Determine device status ─────────────────
        if percentage <= EMPTY_THRESHOLD:
            new_status   = Device.Status.EMPTY
            alert_type   = Device.AlertType.EMPTY
            severity     = Alert.Severity.CRITICAL
            # Below 10% → treat as empty → critical alert
 
        elif percentage <= LOW_THRESHOLD:
            new_status   = Device.Status.LOW
            alert_type   = Device.AlertType.LOW
            severity     = Alert.Severity.WARNING
            # Below 30% → low gas → warning alert
 
        else:
            new_status   = Device.Status.NORMAL
            alert_type   = None
            severity     = None
            # Above 30% → all good → no alert
 
        device.status             = new_status
        device.current_alert_type = alert_type
        device.save()
        # Save all changes to PostgreSQL in one single call
        # More efficient than calling save() multiple times
 
        # ── Step 6: Create alert if needed ──────────────────
        alert_data = None
 
        if alert_type:
            already_active = Alert.objects.filter(
                device=device,
                type=alert_type,
                status=Alert.AlertStatus.ACTIVE
            ).exists()
            # Check if this exact alert type is already active
            # We don't want 500 duplicate LOW alerts for the same cylinder
            # One active alert per type per device at a time
 
            if not already_active:
                alert = Alert.objects.create(
                    device      = device,
                    device_name = device.name,
                    hotel       = device.hotel,
                    type        = alert_type,
                    severity    = severity,
                    status      = Alert.AlertStatus.ACTIVE,
                )
                # Create a new alert row in PostgreSQL
                # device_name stored separately → historical record
 
                alert_data = AlertSerializer(alert).data
                # Convert alert object to JSON dict
                # So we can include it in the response
 
                # ── Step 7: Send Slack notification ─────────
                self._send_slack_alert(device, alert)
 
        # ── Step 8: Return response to ESP32 ────────────────
        return Response(
            {
                'message'      : 'Reading received successfully.',
                'device'       : device.name,
                'weight_kg'    : weight_kg,
                'percentage'   : round(percentage, 1),
                'status'       : device.status,
                'alert_created': alert_data,
            },
            status=status.HTTP_200_OK
        )
 
    def _send_slack_alert(self, device, alert):
        """
        Sends a Slack message to the hotel's channel.
        Only runs if hotel has Slack enabled and webhook URL set.
 
        Prefixed with _ to indicate this is an internal helper method.
        Not an endpoint — only called from post() above.
        """
 
        hotel = device.hotel
 
        if not hotel.slack_enabled or not hotel.slack_webhook_url:
            return
        # Skip silently if Slack is not configured
        # No error — just don't send
 
        import requests
        # Imported here instead of top of file
        # Avoids loading requests library unless Slack is actually needed
 
        message = {
            'text': (
                f"⚠️ *Cylinder Alert — {hotel.name}*\n"
                f"Device   : {device.name}\n"
                f"Location : {device.location}\n"
                f"Type     : {alert.type.upper()}\n"
                f"Severity : {alert.severity.upper()}\n"
                f"Weight   : {device.last_weight}kg remaining\n"
                f"Time     : "
                f"{device.last_seen_at.strftime('%d %b %Y %I:%M %p IST')}"
            )
        }
        # Slack webhook expects JSON with a 'text' key
        # f-strings → embed variable values inside strings using {}
 
        try:
            requests.post(
                hotel.slack_webhook_url,
                json    = message,
                timeout = 5,
            )
            # timeout=5 → give up after 5 seconds
            # Don't let a slow Slack response block the ESP32
 
            alert.last_notified_at = timezone.now()
            alert.save(update_fields=['last_notified_at'])
            # update_fields → only update this one column
            # More efficient than saving the entire row
 
        except Exception:
            pass
            # If Slack fails, don't crash the entire request
            # The weight reading is already saved — that matters most
 
 
# ─────────────────────────────────────────────────────────────
# ALERT VIEWS
# ─────────────────────────────────────────────────────────────
 
class AlertListView(generics.ListAPIView):
    """
    GET /api/alerts/
    GET /api/alerts/?status=active
    GET /api/alerts/?status=resolved
 
    Lists all alerts for this manager's hotel.
    Supports optional filtering by status via URL parameter.
    """
 
    serializer_class   = AlertSerializer
    permission_classes = [IsAuthenticated]
 
    def get_queryset(self):
        queryset = Alert.objects.filter(hotel=self.request.user.hotel)
        # Start with all alerts for this manager's hotel
 
        status_filter = self.request.query_params.get('status')
        # query_params → reads URL parameters
        # /api/alerts/?status=active  → status_filter = 'active'
        # /api/alerts/                → status_filter = None
 
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        # Apply the filter only if parameter was provided
        # .filter() on an existing queryset narrows it further
 
        return queryset
 
 
class AlertResolveView(APIView):
    """
    PATCH /api/alerts/<id>/resolve/
 
    Manager calls this when a cylinder has been refilled.
    Marks the alert as resolved and resets device status.
    """
 
    permission_classes = [IsAuthenticated]
 
    def patch(self, request, pk):
        # pk → the alert ID from the URL e.g. /api/alerts/5/resolve/
        # Django extracts pk automatically from the URL pattern
 
        try:
            alert = Alert.objects.get(
                pk    = pk,
                hotel = request.user.hotel
            )
            # Get the alert by ID AND confirm it belongs to this manager's hotel
            # Prevents a manager from resolving another hotel's alerts
 
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
 
        if alert.status == 'resolved':
            return Response(
                {'error': 'This alert is already resolved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Don't allow resolving something already resolved
 
        # ── Resolve the alert ────────────────────────────────
        alert.status      = Alert.AlertStatus.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['status', 'resolved_at'])
 
        # ── Reset device status back to normal ───────────────
        device                    = alert.device
        device.status             = Device.Status.NORMAL
        device.current_alert_type = None
        device.save(update_fields=['status', 'current_alert_type'])
        # When manager refills the cylinder and resolves the alert,
        # device goes back to NORMAL status automatically
 
        return Response(
            {
                'message'    : f'Alert resolved for {alert.device_name}.',
                'resolved_at': alert.resolved_at,
            },
            status=status.HTTP_200_OK
        )