from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django's built-in admin dashboard
    # You will create hotels here manually for now

    path('api/', include('sensors.urls')),
    # All your API routes are under /api/
    # Example: /api/devices/, /api/alerts/
]