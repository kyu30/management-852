/* This kinda isn't related to the program, it's just explaining the library (came in the template I used)
 * --------------------------------------------------------------------------------------------------------------------
 * Example sketch/program showing how to read data from a PICC to serial.
 * --------------------------------------------------------------------------------------------------------------------
 * This is a MFRC522 library example; for further details and other examples see: https://github.com/miguelbalboa/rfid
 * 
 * Example sketch/program showing how to read data from a PICC (that is: a RFID Tag or Card) using a MFRC522 based RFID
 * Reader on the Arduino SPI interface.
 * 
 * When the Arduino and the MFRC522 module are connected (see the pin layout below), load this sketch into Arduino IDE
 * then verify/compile and upload it. To see the output: use Tools, Serial Monitor of the IDE (hit Ctrl+Shft+M). When
 * you present a PICC (that is: a RFID Tag or Card) at reading distance of the MFRC522 Reader/PCD, the serial output
 * will show the ID/UID, type and any data blocks it can read. Note: you may see "Timeout in communication" messages
 * when removing the PICC from reading distance too early.
 * 
 * If your reader supports it, this sketch/program will read all the PICCs presented (that is: multiple tag reading).
 * So if you stack two or more PICCs on top of each other and present them to the reader, it will first output all
 * details of the first and then the next PICC. Note that this may take some time as all data blocks are dumped, so
 * keep the PICCs at reading distance until complete.
 * 
 * @license Released into the public domain.
 * 
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 */
// imported libraries to use for the program
#include <SPI.h>
#include <MFRC522.h>

// Set which pins on the Arduino board the RFID scanner is connected to 
#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
	Serial.begin(9600);		// Initialize serial communications with the PC
	while (!Serial);		// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
	SPI.begin();			// Init SPI bus
	mfrc522.PCD_Init();		// Init MFRC522
  pinMode(5, OUTPUT); // I used Pins 5 and 6 for the LED lights that I made to respond to the cards
  pinMode(6, OUTPUT);
  pinMode(A5, OUTPUT);
	delay(4);				// Optional delay. Some board do need more time after init to be ready, see Readme
}

void loop() {
	// Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	if ( ! mfrc522.PICC_IsNewCardPresent()) { // Checks if a card is being scanned
		return;
	}

	// Select one of the cards
	if ( ! mfrc522.PICC_ReadCardSerial()) { //Reads the card
		return;
	}

	// Dump debug info about the card; PICC_HaltA() is automatically called
	Serial.print("UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++){ //Loops through the bytes to collect the parts of the card's UID
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println(); // Sends the UID to the serial monitor as a string, we use the serial monitor to communicate with the python script
  delay(1000);
  mfrc522.PICC_HaltA();

  if(Serial.available() > 0){ //Waits for a response from the python script through the serial monitor
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "ACCESS GRANTED"){ //If the Python script sends the ACCESS GRANTED message, the green light turns on 
      digitalWrite(A5, HIGH);
      delay(5000);
      digitalWrite(A5, LOW);
    }
    else if (command == "ACCESS DENIED"){ //If the Python script sends the ACCESS DENIED message, the red light turns on 
      digitalWrite(5, LOW);
      delay(5000)
    }
  }
}
//Wiring diagram not included because I don't actually know how to make one