"""
MOVING BUS SIMULATOR
Simulates 4 buses moving along real GPS routes so the map actually animates.

Run with:
    python simulate_buses.py

Keep it running in a separate terminal while the Django server is also running.
The buses will move on the map automatically every 3 seconds.
"""

import os
import sys
import django
import time
import math

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sarp_t.settings')
django.setup()

from myapp.models import BusLocation, SpeedAlert

# ── Real GPS waypoints for each bus route (Itahari/Eastern Nepal) ──────────
# Each list is a series of GPS points the bus drives through

ROUTES = {
    "bus_01": {
        "name": "Dharan → IIC College",
        "color": "🟢",
        "waypoints": [
            (26.8126, 87.2846),  # Dharan
            (26.7900, 87.2800),
            (26.7650, 87.2760),
            (26.7400, 87.2720),
            (26.7100, 87.2700),
            (26.6900, 87.2700),
            (26.6700, 87.2730),
            (26.6646, 87.2748),  # IIC College
        ],
        "speed_range": (35, 55),
        "occupancy_range": (15, 32),
    },
    "bus_02": {
        "name": "Biratnagar → IIC College",
        "color": "🔵",
        "waypoints": [
            (26.4525, 87.2718),  # Biratnagar
            (26.4800, 87.2730),
            (26.5100, 87.2740),
            (26.5400, 87.2745),
            (26.5700, 87.2746),
            (26.6000, 87.2747),
            (26.6300, 87.2748),
            (26.6646, 87.2748),  # IIC College
        ],
        "speed_range": (40, 60),
        "occupancy_range": (20, 40),
    },
    "bus_03": {
        "name": "Inaruwa → IIC College",
        "color": "🟡",
        "waypoints": [
            (26.6042, 87.1435),  # Inaruwa
            (26.6100, 87.1600),
            (26.6150, 87.1800),
            (26.6200, 87.2000),
            (26.6250, 87.2200),
            (26.6350, 87.2400),
            (26.6500, 87.2600),
            (26.6646, 87.2748),  # IIC College
        ],
        "speed_range": (30, 50),
        "occupancy_range": (8, 22),
    },
    "bus_04": {
        "name": "Itahari Local",
        "color": "🟠",
        "waypoints": [
            (26.6646, 87.2748),  # IIC College
            (26.6700, 87.2800),
            (26.6750, 87.2850),
            (26.6800, 87.2900),
            (26.6750, 87.2950),
            (26.6700, 87.2900),
            (26.6650, 87.2850),
            (26.6646, 87.2748),  # Back to college
        ],
        "speed_range": (15, 30),
        "occupancy_range": (5, 15),
    },
}


def interpolate(p1, p2, t):
    """Return a point t% of the way between p1 and p2."""
    return (
        p1[0] + (p2[0] - p1[0]) * t,
        p1[1] + (p2[1] - p1[1]) * t,
    )


def get_position(waypoints, progress):
    """Given overall progress 0→1, return interpolated GPS position."""
    n = len(waypoints) - 1
    segment = min(int(progress * n), n - 1)
    segment_progress = (progress * n) - segment
    return interpolate(waypoints[segment], waypoints[segment + 1], segment_progress)


class BusSimulator:
    def __init__(self):
        self.positions = {bus_id: 0.0 for bus_id in ROUTES}
        self.directions = {bus_id: 1 for bus_id in ROUTES}  # 1=forward, -1=reverse
        # Stagger starting positions so buses aren't all at the same spot
        self.positions["bus_01"] = 0.1
        self.positions["bus_02"] = 0.3
        self.positions["bus_03"] = 0.6
        self.positions["bus_04"] = 0.8

    def step(self, speed=0.015):
        """Move all buses one step forward."""
        import random

        for bus_id, route in ROUTES.items():
            # Move along route
            self.positions[bus_id] += speed * self.directions[bus_id]

            # Bounce at ends (bus turns around and goes back)
            if self.positions[bus_id] >= 1.0:
                self.positions[bus_id] = 1.0
                self.directions[bus_id] = -1
            elif self.positions[bus_id] <= 0.0:
                self.positions[bus_id] = 0.0
                self.directions[bus_id] = 1

            # Get current GPS position
            lat, lng = get_position(route["waypoints"], self.positions[bus_id])

            # Randomise speed and occupancy slightly
            speed_val = random.uniform(*route["speed_range"])
            occupancy = random.randint(*route["occupancy_range"])

            # Save to database
            BusLocation.objects.create(
                device_id=bus_id,
                lat=round(lat, 7),
                lng=round(lng, 7),
                speed=round(speed_val, 1),
                occupancy=occupancy,
            )

            # Auto speed alert if over 60
            if speed_val > 60:
                SpeedAlert.objects.create(
                    device_id=bus_id,
                    speed=speed_val,
                    lat=lat,
                    lng=lng,
                )
                print(f"  ⚠️  Speed alert: {bus_id} at {speed_val:.1f} km/h")

            progress_pct = int(self.positions[bus_id] * 100)
            direction = "→" if self.directions[bus_id] == 1 else "←"
            print(f"  {route['color']} {bus_id} [{direction} {progress_pct}%] "
                  f"lat={lat:.4f} lng={lng:.4f} "
                  f"speed={speed_val:.0f}km/h occupancy={occupancy}")

        # Clean up old entries — keep only latest 50 per bus
        for bus_id in ROUTES:
            ids_to_keep = list(
                BusLocation.objects.filter(device_id=bus_id)
                .order_by('-timestamp')
                .values_list('id', flat=True)[:50]
            )
            BusLocation.objects.filter(device_id=bus_id).exclude(id__in=ids_to_keep).delete()


def main():
    print("=" * 55)
    print("  SARP-T Bus Simulator — Moving buses on the map")
    print("=" * 55)
    print("  4 buses moving along real Itahari routes")
    print("  Updates every 3 seconds")
    print("  Open http://127.0.0.1:8000 to see them move")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    print()

    sim = BusSimulator()
    tick = 0

    while True:
        tick += 1
        print(f"Tick {tick} — {__import__('datetime').datetime.now().strftime('%H:%M:%S')}")
        sim.step()
        print()
        time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
