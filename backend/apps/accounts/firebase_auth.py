import firebase_admin.auth as firebase_auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class FirebaseUser:
    """A simple user object built from Firebase token — no Django DB needed."""
    def __init__(self, decoded_token):
        self.uid = decoded_token['uid']
        self.email = decoded_token.get('email', '')
        self.full_name = decoded_token.get('name', '')
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return self.email


class FirebaseAuthentication(BaseAuthentication):
    """
    Custom DRF authentication using Firebase ID tokens.
    Expects: Authorization: Bearer <firebase_id_token>
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No token — let permission classes handle it

        token = auth_header.split(' ')[1]

        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise AuthenticationFailed('Token has expired')
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(str(e))

        return (FirebaseUser(decoded_token), token)

    def authenticate_header(self, request):
        return 'Bearer'