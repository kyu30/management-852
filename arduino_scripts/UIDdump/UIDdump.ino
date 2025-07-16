#include <WiFiS3.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "Myhoo";         
const char* password = "6301e89a44"; 
const char* mqtt_server = "192.168.0.106";
const int port = 1883;
const int relayPin = A5;
const String udoor = "Guest";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void callback(char* topic, byte* payload, unsigned int length){

  String message = String((char*)payload).substring(0,length);
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Payload: ");
  Serial.println(message);
  if (String(topic) == "rfid/" + udoor + "/override" || ((String(topic) == "rfid/" + udoor + "/result" && message == "granted"))) {
    unlockDoor();
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
      client.subscribe(("rfid/" + udoor + "/override").c_str());
      client.subscribe(("rfid/" + udoor + "/result").c_str());
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup(){
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
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
  String payload = udoor+ "-" + uid;
  client.publish(("rfid/"+ udoor + "/scan").c_str(), payload.c_str(), true);
  Serial.println("Published to MQTT.");
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(1000);
}

void unlockDoor(){
  Serial.println("Unlocking");
  digitalWrite(relayPin, LOW);
  delay(5000);
  digitalWrite(relayPin, HIGH);
  Serial.println("Locking");
  Serial.println("Reader reset, ready for next scan");
}
