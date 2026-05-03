import firebase_admin
from firebase_admin import credentials, auth
import os


def initialize_firebase():
    """
    Initializes Firebase Admin SDK.
    Called once when Django starts via apps.py ready() method.
    Must run before any request hits the server.
    """

    if not firebase_admin._apps:
        # Check if Firebase is already initialized
        # Prevents duplicate initialization if Django reloads

        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        # Path to your Firebase service account JSON file
        # Set in .env as FIREBASE_CREDENTIALS_PATH

        cred = credentials.Certificate(cred_path)
        # Loads the service account JSON credentials

        firebase_admin.initialize_app(cred)
        # Starts the Firebase Admin SDK
        # After this, verify_firebase_token() will work anywhere


def verify_firebase_token(id_token):
    """
    Verifies a Firebase ID Token sent from the frontend.

    How it works:
    - Frontend logs in with Firebase → gets an ID token
    - Frontend sends that token in every API request header
    - This function sends it to Firebase to check if it's genuine

    Returns:
        dict with uid, email, etc. if token is valid
        None if token is invalid or expired
    """

    try:
        decoded_token = auth.verify_id_token(id_token)
        # Sends token to Firebase servers for verification
        # Firebase checks:
        #   - Is this token genuine? (not fake or tampered)
        #   - Has it expired? (Firebase tokens last 1 hour)
        #   - Does it belong to our project?
        #
        # Returns a dict like:
        # {
        #   "uid": "xK9mP2qL...",
        #   "email": "manager@hotel.com",
        #   "exp": 1234567890
        # }

        return decoded_token

    except auth.ExpiredIdTokenError:
        # Token was valid but has now expired
        # Frontend needs to refresh using Firebase SDK
        return None

    except auth.InvalidIdTokenError:
        # Token is fake, malformed, or from wrong project
        return None

    except Exception:
        # Any other Firebase error (network issue etc.)
        return None