from django.urls import path
from .views import DeviceListCreateView, SensorReadingDetailView, SensorReadingListCreateView

urlpatterns = [
    path("devices/", DeviceListCreateView.as_view(), name="device-list-create"),
    path("readings/", SensorReadingListCreateView.as_view(), name="readings-list-create"),
    path("readings/<str:pk>/", SensorReadingDetailView.as_view(), name="reading-detail"),
]