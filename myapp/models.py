from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, default='')
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.username


class BusLocation(models.Model):
    device_id = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=12, decimal_places=9)
    lng = models.DecimalField(max_digits=12, decimal_places=9)
    speed = models.FloatField(default=0)
    occupancy = models.IntegerField(default=0)   # RFID student count
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device_id} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class TripLog(models.Model):
    device_id = models.CharField(max_length=50)
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    route_name = models.CharField(max_length=100, default='')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.device_id} trip on {self.departure_time}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    bus_id = models.CharField(max_length=50)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Feedback for {self.bus_id} — {self.rating}★"


class SpeedAlert(models.Model):
    device_id = models.CharField(max_length=50)
    speed = models.FloatField()
    lat = models.DecimalField(max_digits=12, decimal_places=9)
    lng = models.DecimalField(max_digits=12, decimal_places=9)
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Alert: {self.device_id} at {self.speed} km/h"
