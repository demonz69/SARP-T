import json
import sys
import os
import django
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# 1. Get the path to the project root (one level up from 'myapp')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Add that path to sys.path so Python can find 'Sarp_t'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sarp_t.settings')
django.setup()

from myapp.models import VehicleLocation

BROKER = "broker.hivemq.com"
TOPIC = "sarp_t/gps/bus01"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        VehicleLocation.objects.update_or_create(
            vehicle_id="bus01",
            defaults={
                "latitude": data["lat"],
                "longitude": data["lng"]
            }
        )
        print("Saved:", data)

    except Exception as e:
        print("Error:", e)

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883)
client.subscribe(TOPIC)
client.on_message = on_message

print("MQTT listening...")
client.loop_forever()
