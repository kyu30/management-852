#include <WiFiS3.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials (Need 2.4 ghz WiFi, won't work with 5 ghz, have to set up w/ ISP)
const char* ssid = "Cubico.co";
const char* password = "cubico123";

// HTTPS server info
const char* server = "management-852-40069d69dc54.herokuapp.com";
int port = 443;
const char* scanner_id = "Guest";

// RFID setup
#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

// Use SSL client for HTTPS
WiFiSSLClient client;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); // Indicator that setup started
  Serial.begin(9600);
  delay(1000);
  Serial.println("Booting...");

  // Init RFID
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("RFID initialized");

  // Connect to WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED && retryCount < 20) {
    delay(500);
    Serial.print(".");
    retryCount++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed");
  }

  digitalWrite(LED_BUILTIN, LOW); // Turn off setup indicator
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    // Build UID string
    String rfidUID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidUID += String(rfid.uid.uidByte[i], HEX);
    }

    Serial.print("Scanned UID: ");
    Serial.println(rfidUID);

    // Connect to HTTPS server
    if (client.connect(server, port)) {
      Serial.println("Connected to server");

      // Construct GET request
      String request = "GET /access_check?rfid=" + rfidUID + "&scanner_id=" + scanner_id + " HTTP/1.1";
      client.println(request);
      client.print("Host: ");
      client.println(server);
      client.println("Connection: close");
      client.println();

      // Read server response
      while (client.connected() || client.available()) {
        if (client.available()) {
          String line = client.readStringUntil('\n');
          Serial.println("Server: " + line);

          if (line.indexOf("Access Granted") >= 0) {
            Serial.println("Door Unlocked");
            // Unlock door logic here
          } else if (line.indexOf("Access Denied") >= 0) {
            Serial.println("Door Locked");
            // Keep door locked logic here
          }
        }
      }

      client.stop();
    } else {
      Serial.println("Failed to connect to server");
    }

    delay(2000); // Debounce
  }
}
