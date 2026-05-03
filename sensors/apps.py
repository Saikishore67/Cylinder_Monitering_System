from django.urls import path
from .views import (
    RegisterView,
    ManagerProfileView,
    DeviceListCreateView,
    DeviceDetailView,
    WeightReadingView,
    AlertListView,
    AlertResolveView,
)

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view()),
    # POST → create Django manager account after Firebase signup
    # Body: { "uid": "firebaseUID", "hotel": 1 }
    # No token required

    path('auth/profile/', ManagerProfileView.as_view()),
    # GET → returns logged-in manager's profile + hotel info
    # Requires: Firebase token in Authorization header

    # ── Devices ───────────────────────────────────────────────
    path('devices/', DeviceListCreateView.as_view()),
    # GET  → list all devices for this manager's hotel
    # POST → register a new ESP32 device
    # Body: { "device_id": "ESP32-A1B2", "name": "...", "location": "..." }

    path('devices/<int:pk>/', DeviceDetailView.as_view()),
    # GET    → view full details of one device
    # PATCH  → update device name or location
    # DELETE → remove device from system
    # <int:pk> → Django extracts device ID from URL automatically

    # ── Weight Readings (ESP32 posts here) ────────────────────
    path('readings/', WeightReadingView.as_view()),
    # POST → ESP32 sends weight data
    # Body: { "device_id": "ESP32-A1B2", "weight_kg": 4.2 }
    # No auth token required — device uses device_id

    # ── Alerts ────────────────────────────────────────────────
    path('alerts/', AlertListView.as_view()),
    # GET → list all alerts for this hotel
    # Optional filter: /api/alerts/?status=active
    #                  /api/alerts/?status=resolved

    path('alerts/<int:pk>/resolve/', AlertResolveView.as_view()),
    # PATCH → mark alert as resolved (cylinder was refilled)
    # No body needed — just call the endpoint
]