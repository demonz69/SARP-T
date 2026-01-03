from django.shortcuts import render
from django.http import JsonResponse
from .models import BusLocation

def home(request):
    return render(request, 'myapp/index.html')

def about(request):
    return render(request, 'myapp/about.html')

# This view serves the actual HTML page
def map_view(request):
    return render(request, 'map.html')

# This view serves the latest coordinates as JSON
def get_latest_location(request):
    # Get the latest entry for bus_01
    latest_data = BusLocation.objects.filter(device_id="bus_01").order_by('-timestamp').first()
    
    if latest_data:
        return JsonResponse({
            "lat": float(latest_data.lat),
            "lng": float(latest_data.lng),
            "speed": latest_data.speed,
            "timestamp": latest_data.timestamp.strftime("%H:%M:%S")
        })
    return JsonResponse({"error": "No data available"}, status=404)