#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// --- Configuration ---
const char* ssid = "harka2_wnepal";
const char* password = "basnet@123";
const char* mqtt_server = "test.mosquitto.org"; // Public Broker

// GPS Pins: RX=D6, TX=D7 (NodeMCU)
// Connect GPS TX to D6, GPS RX to D7
SoftwareSerial gpsSerial(12, 13); 
TinyGPSPlus gps;
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600);
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266_Bus_01")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void publishGPSData() {
  // Create JSON document
  StaticJsonDocument<200> doc;
  doc["device_id"] = "bus_01";
  doc["lat"] = gps.location.lat();
  doc["lng"] = gps.location.lng();
  doc["speed"] = gps.speed.kmph();

  char buffer[256];
  serializeJson(doc, buffer);

  Serial.print("Publishing: ");
  Serial.println(buffer);
  client.publish("bus/gps", buffer);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read data from GPS Module
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      // Send data every 5 seconds if location is valid
      unsigned long now = millis();
      if (now - lastMsg > 5000) {
        lastMsg = now;
        if (gps.location.isValid()) {
          publishGPSData();
        } else {
          Serial.println("Waiting for GPS signal (Satellite Fix)...");
        }
      }
    }
  }
}