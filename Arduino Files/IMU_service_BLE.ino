#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

// BLE Service for IMU Data
BLEService imuService("180C");

// BLE Characteristics for Acceleration and Gyroscope data
BLEStringCharacteristic accelerationCharacteristic("2A58", BLERead | BLENotify, 20);
BLEStringCharacteristic gyroscopeCharacteristic("2A59", BLERead | BLENotify, 20);
BLEStringCharacteristic switchCharacteristic("2A60", BLERead | BLENotify, 20);


enum Mode{
  IDLING,
  RECORDING
};

Mode current_mode = IDLING;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE");
  BLE.setAdvertisedService(imuService);

  // add characteristics
  imuService.addCharacteristic(accelerationCharacteristic);
  imuService.addCharacteristic(gyroscopeCharacteristic);

  // add service
  BLE.addService(imuService);

  // start advertising
  BLE.advertise();

  Serial.println("Bluetooth device active, waiting for connections...");
}

void loop() {
  // wait for a BLE central
  BLEDevice central = BLE.central();

  // if a central is connected to the peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    // while the central is still connected to the peripheral:
    while (central.connected()) {
        if (switchCharacteristic.written() && current_mode == IDLING  ) {
          
          
          }


      
      float x, y, z;

      // read acceleration
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(x, y, z);
        String accData = String(x) + "," + String(y) + "," + String(z);
        accelerationCharacteristic.writeValue(accData);
      }

      // read gyroscope
      if (IMU.gyroscopeAvailable()) {
        IMU.readGyroscope(x, y, z);
        String gyroData = String(x) + "," + String(y) + "," + String(z);
        gyroscopeCharacteristic.writeValue(gyroData);
      }

      // Delay to not flood with data; adjust as needed based on your requirements
      delay(100);
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
}
  
