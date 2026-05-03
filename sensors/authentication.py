from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .firebase import verify_firebase_token
from .models import CustomUser


class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication class for Django REST Framework.

    Django REST Framework calls authenticate() on every request
    before the view runs. This replaces JWT entirely.

    Flow:
    1. Frontend logs in with Firebase → gets ID token
    2. Frontend sends: Authorization: Bearer <id_token>
    3. This class extracts and verifies that token
    4. Finds the matching manager in PostgreSQL
    5. Sets request.user so views can use it
    """

    def authenticate(self, request):
        """
        Called automatically by DRF on every request.

        Returns:
            (user, None) if authentication succeeds
            None if no token in header (let DRF decide what to do)

        Raises:
            AuthenticationFailed if token is present but invalid
        """

        auth_header = request.headers.get('Authorization')
        # Read the Authorization header from the request
        # Expected format: "Bearer eyJhbGci..."

        if not auth_header:
            return None
        # No header at all → unauthenticated request
        # Return None and let DRF handle it
        # If endpoint has IsAuthenticated, DRF will block it

        if not auth_header.startswith('Bearer '):
            return None
        # Header exists but wrong format — skip it

        id_token = auth_header.split('Bearer ')[1].strip()
        # "Bearer eyJhbGci..." → "eyJhbGci..."
        # .strip() removes any extra whitespace

        if not id_token:
            raise AuthenticationFailed('Token is empty.')

        decoded_token = verify_firebase_token(id_token)
        # Send to Firebase for verification
        # Returns decoded data or None

        if not decoded_token:
            raise AuthenticationFailed(
                'Firebase token is invalid or expired. Please log in again.'
            )
        # Reject the request — DRF returns 401 Unauthorized

        uid = decoded_token.get('uid')
        # Extract Firebase UID from decoded token

        if not uid:
            raise AuthenticationFailed('Token is missing user ID.')

        try:
            user = CustomUser.objects.get(uid=uid)
            # Find the manager in PostgreSQL using Firebase UID
            # This links their Firebase identity to your app data

        except CustomUser.DoesNotExist:
            raise AuthenticationFailed(
                'No manager account found. Please register first.'
            )
        # Firebase knows this person but Django doesn't
        # Manager must call /api/auth/register/ first

        return (user, None)
        # Return (user, token) tuple — DRF requirement
        # After this, request.user = user in every view
        # None for token — we don't store tokens server-side