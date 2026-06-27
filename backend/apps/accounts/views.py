from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from google.cloud import firestore
from google.oauth2 import service_account
from decouple import config
from .serializers import FirebaseTokenSerializer
from datetime import datetime, timezone

# Initialize Firestore with Firebase credentials
credentials = service_account.Credentials.from_service_account_file(
    config('FIREBASE_CREDENTIALS')
)

db = firestore.Client(
    project=config('FIRESTORE_PROJECT_ID'),
    credentials=credentials
)

class FirebaseLoginView(APIView):
    """
    Receives Firebase token from frontend.
    Verifies it, creates user in Firestore if new, returns user data.
    """
    permission_classes = [AllowAny]
    serializer_class = FirebaseTokenSerializer

    def post(self, request):
        import firebase_admin.auth as firebase_auth

        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')

        # Check if user exists in Firestore
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            # Create new user in Firestore
            user_data = {
                'uid': uid,
                'email': email,
                'full_name': name,
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
            user_ref.set(user_data)
            created = True
        else:
            user_data = user_doc.to_dict()
            created = False

        return Response(
            {
                'user': user_data,
                'created': created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    Returns current authenticated user's data from Firestore.
    Requires Firebase token in Authorization header.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        uid = request.user.uid

        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(user_doc.to_dict(), status=status.HTTP_200_OK)