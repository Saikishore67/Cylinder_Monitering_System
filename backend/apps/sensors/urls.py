from django.urls import path
from .views import DeviceListCreateView, SensorReadingDetailView, SensorReadingListCreateView

urlpatterns = [
    path("readings/", SensorReadingListCreateView.as_view(), name="readings-list-create"),
    path("readings/<int:pk>/", SensorReadingDetailView.as_view(), name="reading-detail"),
    path("devices/", DeviceListCreateView.as_view(), name="device-list"),
]