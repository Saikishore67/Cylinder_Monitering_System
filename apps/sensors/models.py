from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Device(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="devices",
    )

    name = models.CharField(max_length=100)

    device_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class SensorReading(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="readings",
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
    )

    timestamp = models.DateTimeField()

    data = models.JSONField(
        default=dict,
        blank=True,
    )

    received_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-timestamp"]

        indexes = [
            models.Index(fields=["device", "-timestamp"]),
        ]

    def __str__(self):
        return (
            f"{self.device.name} "
            f"({self.device.device_id}) "
            f"@ {self.timestamp} "
            f"— {self.weight}kg"
        )