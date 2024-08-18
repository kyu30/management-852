#include <WiFiS3.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "Myhoo";
const char* password = "6301e89a44";
WiFiClient client;
const char * server = "192.168.0.108";
//const char* server = "https://management-852-659211fd36ae.herokuapp.com";
//int port = 443;
int port = 5000;
const char* scanner_id = "Guest";

// Define RFID pins
#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);


void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Setup RFID
  SPI.begin();
  rfid.PCD_Init();

  // Connect to WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("Connected to WiFi");
  Serial.print("Arduino IP address: ");
  Serial.println(WiFi.localIP());
  }

void loop() {
  // Look for new cards
  if (rfid.PICC_IsNewCardPresent()) {
    // Select one of the cards
    if (rfid.PICC_ReadCardSerial()) {
      String rfidUID = "";
      for (byte i = 0; i < rfid.uid.size; i++) {
        rfidUID += String(rfid.uid.uidByte[i], HEX);
      }
      Serial.println(rfidUID); // Print UID to Serial Monitor

      // Send the UID to the Flask server
      if (client.connect(server, port)) {
        Serial.println("Connected to server");
        String url = "GET /access_check?rfid=" + String(rfidUID) + "&scanner_id=" + String(scanner_id) + " HTTP/1.1";
        Serial.println(url);
        client.println(url);
        client.println("Host: " );
        client.print(server);
        client.println("Connection: close");
        client.println();
      
        // Read the response from the server
        String response = "";
        while (client.connected() || client.available()) {
          if (client.available()) {
            String response = client.readStringUntil('\n');
            Serial.println("Response from server: "+ response);

            // Act on the response
            if (response.indexOf("Access Granted") >= 0) {
              Serial.println("Door Unlocked");
              // Add your code to unlock the door here
            } else if (response.indexOf("Access Denied") >= 0) {
              Serial.println("Door Locked");
              // Add your code to keep the door locked here
            }
          }
        }

        client.stop();
      }

      delay(2000); // Prevent multiple reads
    }
  }
}