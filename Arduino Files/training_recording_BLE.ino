#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#define SAMPLES 200  // 100Hz for 2 seconds

float ax[SAMPLES], ay[SAMPLES], az[SAMPLES]; // Accelerometer data arrays
float gx[SAMPLES], gy[SAMPLES], gz[SAMPLES]; // Gyroscope data arrays

BLEService imuService("180C"); // Custom service for IMU data
BLECharacteristic accCharacteristic("2A58", BLERead | BLENotify, 12 * SAMPLES); // 12 = 3 axes * 4 bytes each, for all samples
BLECharacteristic gyroCharacteristic("2A59", BLERead  | BLENotify, 12 * SAMPLES); // Same size for gyroscope data
BLECharacteristic commandCharacteristic("2A60", BLEWrite, 20); // A characteristic for receiving commands

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE");
  BLE.setAdvertisedService(imuService);
  imuService.addCharacteristic(accCharacteristic);
  imuService.addCharacteristic(gyroCharacteristic);
  imuService.addCharacteristic(commandCharacteristic);

  BLE.addService(imuService);
  BLE.advertise();

  Serial.println("Ready to connect. Send 'start' to begin data collection.");
}


void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.println("Connected to central");

    while (central.connected()) {
      if (commandCharacteristic.written()) {
        // Get the value as a binary data
        uint8_t* data = (uint8_t*)commandCharacteristic.value();
        int length = commandCharacteristic.valueLength(); // Get the data length

        // Convert binary data to String
        String command = "";
        for (int i = 0; i < length; i++) {
          command += (char)data[i];
        }

        // Check if the command is "start"
        if (command == "start") {
          Serial.println("Starting data collection");
          collectIMUData();
          sendData();
        }
      }
    }
  }
}



void collectIMUData() {
  Serial.println("Collecting IMU data...");
  for (int i = 0; i < SAMPLES; i++) {
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(ax[i], ay[i], az[i]);
    }
    if (IMU.gyroscopeAvailable()) {
      IMU.readGyroscope(gx[i], gy[i], gz[i]);
    }
    delay(10); // Collect at 100Hz
  }
}
void sendData() {
  Serial.println("Sending data...");
  // Buffer to hold the index (2 bytes) + 3 floats (4 bytes each)
  uint8_t dataBuffer[2 + 3 * 4];

  for (int i = 0; i < SAMPLES; i++) {
    // Populate the buffer with the sample index (i)
    dataBuffer[0] = (i >> 8) & 0xFF; // High byte of the index
    dataBuffer[1] = i & 0xFF;        // Low byte of the index

    // Copy the accelerometer data into the buffer
    memcpy(&dataBuffer[2], &ax[i], 4);
    memcpy(&dataBuffer[6], &ay[i], 4);
    memcpy(&dataBuffer[10], &az[i], 4);
    // Notify with the accelerometer data + index
    accCharacteristic.writeValue(dataBuffer, sizeof(dataBuffer));

    // Copy the gyroscope data into the buffer (reuse the same index for simplicity)
    memcpy(&dataBuffer[2], &gx[i], 4);
    memcpy(&dataBuffer[6], &gy[i], 4);
    memcpy(&dataBuffer[10], &gz[i], 4);
    // Notify with the gyroscope data + index
    gyroCharacteristic.writeValue(dataBuffer, sizeof(dataBuffer));

    delay(10); // Adjust based on BLE throughput and reliability
  }
  Serial.println("Data sent.");
}
