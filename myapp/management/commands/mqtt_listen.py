import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from myapp.models import BusLocation, SpeedAlert

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "bus/gps"          # Must match ESP8266 publish topic
SPEED_LIMIT = 60


class Command(BaseCommand):
    help = 'Starts MQTT subscriber — listens for GPS data from buses'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Connecting to MQTT Broker...'))

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                self.stdout.write(self.style.SUCCESS(f'Connected! Subscribed to: {MQTT_TOPIC}'))
                client.subscribe(MQTT_TOPIC)
            else:
                self.stdout.write(self.style.ERROR(f'Connection failed: {reason_code}'))

        def on_message(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode('utf-8'))
                self.stdout.write(f"Received: {data}")

                entry = BusLocation.objects.create(
                    device_id=data['device_id'],
                    lat=data['lat'],
                    lng=data['lng'],
                    speed=data.get('speed', 0),
                    occupancy=data.get('occupancy', 0),
                )

                if entry.speed > SPEED_LIMIT:
                    SpeedAlert.objects.create(
                        device_id=entry.device_id,
                        speed=entry.speed,
                        lat=entry.lat,
                        lng=entry.lng,
                    )
                    self.stdout.write(self.style.WARNING(
                        f'SPEED ALERT: {entry.device_id} at {entry.speed} km/h!'
                    ))

                self.stdout.write(self.style.SUCCESS(f'Saved: {entry}'))

            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'Missing field in payload: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {e}'))

        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        self.stdout.write('Listening for GPS data... (Ctrl+C to stop)')
        client.loop_forever()
