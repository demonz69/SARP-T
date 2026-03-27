import math
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils import timezone
import json

from .models import BusLocation, CustomUser, TripLog, Feedback, SpeedAlert

SPEED_LIMIT_KMPH = 60


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ── Auth ──────────────────────────────────────────────────────

def home(request):
    return render(request, 'myapp/index.html')


@ensure_csrf_cookie
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username  = request.POST.get('username', '').strip()
        password  = request.POST.get('password', '')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        user = CustomUser.objects.create_user(
            username=username, password=password,
            full_name=full_name, role='student'
        )
        login(request, user)
        return redirect('dashboard')
    return render(request, 'myapp/register.html')


@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'myapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Dashboard — routes by role ────────────────────────────────

@login_required(login_url='login')
def dashboard_view(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    return render(request, 'myapp/map.html')


# ── Student / Bus APIs ────────────────────────────────────────

@login_required(login_url='login')
def get_latest_location(request):
    device_id = request.GET.get('device_id', None)
    qs = BusLocation.objects.all()
    if device_id:
        qs = qs.filter(device_id=device_id)
    seen = {}
    for entry in qs:
        if entry.device_id not in seen:
            seen[entry.device_id] = entry
    buses = [{
        'device_id': b.device_id,
        'lat': float(b.lat),
        'lng': float(b.lng),
        'speed': b.speed,
        'occupancy': b.occupancy,
        'timestamp': b.timestamp.strftime('%H:%M:%S'),
    } for b in seen.values()]
    if device_id and buses:
        return JsonResponse(buses[0])
    return JsonResponse({'buses': buses})


@login_required(login_url='login')
def get_eta(request):
    device_id  = request.GET.get('device_id', 'bus_01')
    target_lat = float(request.GET.get('lat', 26.6646))
    target_lng = float(request.GET.get('lng', 87.2748))
    bus = BusLocation.objects.filter(device_id=device_id).first()
    if not bus:
        return JsonResponse({'eta_minutes': None, 'error': 'No data'})
    dist_km = haversine_km(float(bus.lat), float(bus.lng), target_lat, target_lng)
    speed = bus.speed if bus.speed > 2 else 30
    eta_minutes = round((dist_km / speed) * 60)
    return JsonResponse({
        'eta_minutes': eta_minutes,
        'distance_km': round(dist_km, 2),
        'current_speed': bus.speed,
    })


@csrf_exempt
def receive_gps(request):
    """ESP8266 POSTs GPS data here."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        entry = BusLocation.objects.create(
            device_id=data['device_id'],
            lat=data['lat'],
            lng=data['lng'],
            speed=data.get('speed', 0),
            occupancy=data.get('occupancy', 0),
        )
        if entry.speed > SPEED_LIMIT_KMPH:
            SpeedAlert.objects.create(
                device_id=entry.device_id,
                speed=entry.speed,
                lat=entry.lat,
                lng=entry.lng,
            )
        return JsonResponse({'status': 'ok', 'id': entry.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def submit_feedback(request):
    if request.method == 'POST':
        bus_id  = request.POST.get('bus_id', '').strip()
        rating  = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '').strip()
        if bus_id and comment:
            Feedback.objects.create(
                user=request.user, bus_id=bus_id,
                rating=rating, comment=comment,
            )
            return JsonResponse({'status': 'ok', 'message': 'Feedback submitted. Thank you!'})
        return JsonResponse({'status': 'error', 'message': 'Please fill in all fields.'}, status=400)
    return JsonResponse({'error': 'POST only'}, status=405)


@login_required(login_url='login')
def acknowledge_alert(request, alert_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    SpeedAlert.objects.filter(id=alert_id).update(acknowledged=True)
    return JsonResponse({'status': 'ok'})
