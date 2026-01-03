import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from myapp.models import BusLocation

# MQTT Settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "bus/gps"

class Command(BaseCommand):
    help = 'Starts the MQTT subscriber to listen for GPS data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Connecting to MQTT Broker...'))

        # This is for paho-mqtt version 2.0+
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                self.stdout.write(self.style.SUCCESS("✅ Connected to MQTT Broker!"))
                client.subscribe(MQTT_TOPIC)
            else:
                self.stdout.write(self.style.ERROR(f"❌ Connection failed: {reason_code}"))

        def on_message(client, userdata, msg):
            try:
                # 1. Decode the message from ESP8266
                payload = json.loads(msg.payload.decode('utf-8'))
                
                # 2. Print it to the console so you can see it working
                print(f"Received data: {payload}")

                # 3. Save it to your MySQL Database
                BusLocation.objects.create(
                    device_id=payload['device_id'],
                    lat=payload['lat'],
                    lng=payload['lng'],
                    speed=payload['speed']
                )
                
                self.stdout.write(self.style.SUCCESS(f"Successfully saved to DB"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))

        # Initialize the MQTT Client
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start the loop to listen forever
        client.loop_forever()