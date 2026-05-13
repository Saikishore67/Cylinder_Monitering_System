from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Device, SensorReading

from .serializers import (
    DeviceSerializer,
    SensorReadingCreateSerializer,
    SensorReadingSerializer,
)


@extend_schema(
    request=DeviceSerializer,
    responses=DeviceSerializer,
)
class DeviceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(owner=request.user)

        serializer = DeviceSerializer(
            devices,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = DeviceSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(owner=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    request=SensorReadingCreateSerializer,
    responses=SensorReadingSerializer,
)
class SensorReadingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = SensorReading.objects.filter(
            device__owner=request.user
        )

        device_id = request.query_params.get(
            "device_id"
        )

        if device_id:
            qs = qs.filter(
                device__device_id=device_id
            )

        serializer = SensorReadingSerializer(
            qs,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = SensorReadingCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            reading = serializer.save()

            return Response(
                SensorReadingSerializer(reading).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    responses=SensorReadingSerializer,
)
class SensorReadingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return SensorReading.objects.get(
                pk=pk,
                device__owner=user,
            )

        except SensorReading.DoesNotExist:
            return None

    def get(self, request, pk):
        reading = self.get_object(
            pk,
            request.user,
        )

        if not reading:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            SensorReadingSerializer(reading).data
        )