#include <WiFiS3.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "Myhoo";         
const char* password = "6301e89a44"; 
const char* mqtt_server = "192.168.0.105";
const int port = 1883;

//RELAY_PIN = 5 //Change this later for lock

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void callback(char* topic, byte* payload, unsigned int length){
  String message = "";
  for (unsigned int i = 0; i <length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message received on topic [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  if (message = "Access Granted") {
    Serial.println("Access granted. Unlocking...");
    //digitalWrite(RELAY_PIN, HIGH);
    delay(5000);
  } else if (message == "Access Denied") {
    Serial.println("Access denied");

  }
}

#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup_wifi(){
  Serial.print("Connecting to Wifi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  delay(1000);
  Serial.println("\nWiFi connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect(){
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("Office")) {
      Serial.println("Connected.");
      client.subscribe("door/control");
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup(){
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.println("Ready to scan");
}

void loop(){
  if (!client.connected()){
    reconnect();
  }
  client.loop();
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()){
    return;
  }
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i  <mfrc522.uid.size - 1) uid += " ";
  }
  uid.toUpperCase();

  Serial.print("Card UID: ");
  Serial.println(uid);

  String payload = "Guest-" + uid;
  client.publish("rfid/Guest", payload.c_str(), true);
  Serial.println("Published to MQTT.");

  delay(2000);
}
