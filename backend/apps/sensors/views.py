from datetime import datetime, timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from google.cloud import firestore
from google.oauth2 import service_account
from decouple import config
from .serializers import DeviceSerializer, SensorReadingCreateSerializer, SensorReadingSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter



# Initialize Firestore
credentials = service_account.Credentials.from_service_account_file(
    config('FIREBASE_CREDENTIALS')
)
db = firestore.Client(
    project=config('FIRESTORE_PROJECT_ID'),
    credentials=credentials
)


class DeviceListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

    def get(self, request):
        uid = request.user.uid

        devices_ref = db.collection('users').document(uid).collection('devices')
        devices = [doc.to_dict() for doc in devices_ref.stream()]

        return Response(devices, status=status.HTTP_200_OK)

    def post(self, request):
        uid = request.user.uid
        name = request.data.get('name')
        device_id = request.data.get('device_id')

        if not name or not device_id:
            return Response(
                {'error': 'name and device_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device_ref = db.collection('users').document(uid).collection('devices').document(device_id)

        if device_ref.get().exists:
            return Response(
                {'error': 'Device with this device_id already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device_data = {
            'name': name,
            'device_id': device_id,
            'owner_uid': uid,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }

        device_ref.set(device_data)

        return Response(device_data, status=status.HTTP_201_CREATED)

@extend_schema(
    parameters=[
        OpenApiParameter(name='device_id', type=str, required=True, description='Device ID to filter readings')
    ]
)
class SensorReadingListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SensorReadingCreateSerializer

    def get(self, request):
        uid = request.user.uid
        device_id = request.query_params.get('device_id')

        if not device_id:
            return Response(
                {'error': 'device_id query param is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        readings_ref = (
            db.collection('users')
            .document(uid)
            .collection('devices')
            .document(device_id)
            .collection('readings')
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
        )

        readings = []
        for doc in readings_ref.stream():
            reading = doc.to_dict()
            reading['id'] = doc.id
            readings.append(reading)

        return Response(readings, status=status.HTTP_200_OK)

    def post(self, request):
        uid = request.user.uid
        device_id = request.data.get('device_id')
        weight = request.data.get('weight')
        timestamp = request.data.get('timestamp', datetime.now(timezone.utc).isoformat())
        data = request.data.get('data', {})

        if not device_id or weight is None:
            return Response(
                {'error': 'device_id and weight are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if float(weight) < 0:
            return Response(
                {'error': 'Weight cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check device exists
        device_ref = db.collection('users').document(uid).collection('devices').document(device_id)
        if not device_ref.get().exists:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        reading_data = {
            'device_id': device_id,
            'weight': weight,
            'timestamp': timestamp,
            'data': data,
            'received_at': datetime.now(timezone.utc).isoformat(),
        }

        # Auto generate reading ID
        reading_ref = device_ref.collection('readings').document()
        reading_ref.set(reading_data)
        reading_data['id'] = reading_ref.id

        return Response(reading_data, status=status.HTTP_201_CREATED)

@extend_schema(
    parameters=[
        OpenApiParameter(name='device_id', type=str, required=True, description='Device ID of the reading')
    ]
)
class SensorReadingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SensorReadingSerializer
    def get(self, request, pk):
        uid = request.user.uid
        device_id = request.query_params.get('device_id')

        if not device_id:
            return Response(
                {'error': 'device_id query param is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reading_ref = (
            db.collection('users')
            .document(uid)
            .collection('devices')
            .document(device_id)
            .collection('readings')
            .document(pk)
        )

        reading = reading_ref.get()

        if not reading.exists:
            return Response(
                {'error': 'Reading not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(reading.to_dict(), status=status.HTTP_200_OK)