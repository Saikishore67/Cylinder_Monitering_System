from django.urls import path
from .views import MeView, FirebaseLoginView

urlpatterns = [
    path("firebase-login/", FirebaseLoginView.as_view(), name="firebase_login"),
    path("me/", MeView.as_view(), name="me"),
]