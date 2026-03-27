"""
Run this to fill your database with fake demo data:
    python manage.py shell < seed_data.py

This creates:
- 5 student accounts
- 2 driver accounts
- Fake GPS locations for bus_01 to bus_04
- Fake RFID occupancy counts
- Trip logs for all 4 buses
- Speed alerts
- Student feedback
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sarp_t.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
import random
from myapp.models import CustomUser, BusLocation, TripLog, Feedback, SpeedAlert

print("Seeding database with demo data...")

# ── Students ──────────────────────────────────────────────────
students = [
    {"username": "ram_sharma",   "full_name": "Ram Sharma",    "password": "student123"},
    {"username": "sita_thapa",   "full_name": "Sita Thapa",    "password": "student123"},
    {"username": "hari_adhikari","full_name": "Hari Adhikari", "password": "student123"},
    {"username": "gita_basnet",  "full_name": "Gita Basnet",   "password": "student123"},
    {"username": "bishal_rai",   "full_name": "Bishal Rai",    "password": "student123"},
]

for s in students:
    if not CustomUser.objects.filter(username=s["username"]).exists():
        CustomUser.objects.create_user(
            username=s["username"],
            password=s["password"],
            full_name=s["full_name"],
            role="student"
        )
        print(f"  Created student: {s['full_name']}")

# ── Drivers ───────────────────────────────────────────────────
drivers = [
    {"username": "driver_ram",   "full_name": "Ram Bahadur (Driver)", "password": "driver123"},
    {"username": "driver_shyam", "full_name": "Shyam Prasad (Driver)","password": "driver123"},
]
for d in drivers:
    if not CustomUser.objects.filter(username=d["username"]).exists():
        CustomUser.objects.create_user(
            username=d["username"],
            password=d["password"],
            full_name=d["full_name"],
            role="driver"
        )
        print(f"  Created driver: {d['full_name']}")

# ── Bus GPS locations ─────────────────────────────────────────
# Coordinates around Itahari / Eastern Nepal area
bus_locations = [
    # bus_01 — Dharan route
    {"device_id": "bus_01", "lat": 26.8126, "lng": 87.2846, "speed": 42.5, "occupancy": 18},
    # bus_02 — Biratnagar route
    {"device_id": "bus_02", "lat": 26.4525, "lng": 87.2718, "speed": 38.0, "occupancy": 25},
    # bus_03 — Inaruwa route
    {"device_id": "bus_03", "lat": 26.6042, "lng": 87.1435, "speed": 55.0, "occupancy": 12},
    # bus_04 — Itahari local
    {"device_id": "bus_04", "lat": 26.6646, "lng": 87.2748, "speed": 22.0, "occupancy": 8},
]

for b in bus_locations:
    BusLocation.objects.create(**b)
    print(f"  Created GPS location for {b['device_id']} — {b['occupancy']} passengers on board")

# ── Trip logs ─────────────────────────────────────────────────
trips = [
    {"device_id": "bus_01", "route_name": "Dharan to IIC College",    "departure_time": timezone.now() - timedelta(hours=2), "arrival_time": timezone.now() - timedelta(hours=1),    "notes": "On time"},
    {"device_id": "bus_02", "route_name": "Biratnagar to IIC College","departure_time": timezone.now() - timedelta(hours=3), "arrival_time": timezone.now() - timedelta(minutes=90),"notes": "5 min delay due to traffic"},
    {"device_id": "bus_03", "route_name": "Inaruwa to IIC College",   "departure_time": timezone.now() - timedelta(hours=1), "arrival_time": None,                                   "notes": "Currently en route"},
    {"device_id": "bus_04", "route_name": "Itahari Local",            "departure_time": timezone.now() - timedelta(minutes=30), "arrival_time": None,                               "notes": ""},
]

for t in trips:
    TripLog.objects.create(**t)
    print(f"  Created trip log: {t['route_name']}")

# ── Speed alerts ──────────────────────────────────────────────
SpeedAlert.objects.create(
    device_id="bus_03",
    speed=72.4,
    lat=26.6042,
    lng=87.1435,
    triggered_at=timezone.now() - timedelta(minutes=45),
    acknowledged=False,
)
SpeedAlert.objects.create(
    device_id="bus_01",
    speed=68.1,
    lat=26.8126,
    lng=87.2846,
    triggered_at=timezone.now() - timedelta(hours=1, minutes=20),
    acknowledged=True,
)
print("  Created 2 speed alerts (1 active, 1 dismissed)")

# ── Student feedback ──────────────────────────────────────────
student = CustomUser.objects.filter(role='student').first()
feedbacks = [
    {"bus_id": "bus_01", "rating": 5, "comment": "Driver was very professional and bus was on time!"},
    {"bus_id": "bus_02", "rating": 4, "comment": "Good service but slightly delayed today."},
    {"bus_id": "bus_03", "rating": 3, "comment": "Bus was a bit crowded this morning."},
    {"bus_id": "bus_01", "rating": 5, "comment": "Clean bus and smooth ride. Very happy!"},
    {"bus_id": "bus_04", "rating": 4, "comment": "Comfortable journey, appreciate the service."},
]
for fb in feedbacks:
    Feedback.objects.create(user=student, **fb)
    print(f"  Created feedback for {fb['bus_id']}: {fb['rating']}★")

print("\nDone! Demo data loaded successfully.")
print("\nStudent login:  username=ram_sharma  password=student123")
print("Driver login:   username=driver_ram  password=driver123")
