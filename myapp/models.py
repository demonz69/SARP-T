from django.db import models

class VehicleLocation(models.Model):
    vehicle_id = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vehicle_id
