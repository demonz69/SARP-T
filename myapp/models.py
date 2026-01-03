from django.db import models

class BusLocation(models.Model):
    device_id = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=12, decimal_places=9)
    lng = models.DecimalField(max_digits=12, decimal_places=9)
    speed = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.timestamp}"