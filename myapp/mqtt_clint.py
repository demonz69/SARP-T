import json
import sys
import os
import django
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# ─── Django Environment Setup ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Points Django to the correct settings module before calling setup()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sarp_t.settings')

django.setup()

from myapp.models import BusLocationLocation

# ─── MQTT Configuration ──────────────────────────────────────────────────────
BROKER = "test.mosquitto.org"  
TOPIC  = "sarp_t/gps/bus01"     


# ─── Message Handler (Callback) ──────────────────────────────────────────────
def on_message(client, userdata, msg):
    """
    Triggered automatically whenever a message is received on the subscribed topic.
    Parses the incoming JSON payload and upserts the bus location into the database.
    """
    try:
        data = json.loads(msg.payload.decode())

        # Upserts the bus location:
        BusLocationLocation.objects.update_or_create(
            vehicle_id="bus01",
            defaults={
                "latitude":  data["lat"],
                "longitude": data["lng"]
            }
        )
        print("Saved:", data)

    except Exception as e:
    
        print("Error:", e)


# ─── MQTT Client Initialization & Event Loop ─────────────────────────────────

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883)
client.subscribe(TOPIC)

client.on_message = on_message
print("MQTT listening...")

