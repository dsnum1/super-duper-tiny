
/* Edge Impulse ingestion SDK
 * Copyright (c) 2022 EdgeImpulse Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

/* Includes ---------------------------------------------------------------- */
#include <cricket-tings_inferencing.h>
#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>


//
//
//BLEService shotService("180C");
//BLEStringCharacteristic inferenceCharacteristic("2A58", BLERead | BLENotify, 20);



enum Mode{
  IDLING,
  RECORDING
};

Mode current_mode = IDLING;

float features[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE] = {0};

/**
 * @brief      Copy raw feature data in out_ptr
 *             Function called by inference library
 *
 * @param[in]  offset   The offset
 * @param[in]  length   The length
 * @param      out_ptr  The out pointer
 *
 * @return     0
 */
int raw_feature_get_data(size_t offset, size_t length, float *out_ptr) {
    memcpy(out_ptr, features + offset, length * sizeof(float));
    return 0;
}

void print_inference_result(ei_impulse_result_t result);

/**
 * @brief      Arduino setup function
 */
void setup() {
    Serial.begin(921600);
    while (!Serial);

    Serial.println("Edge Impulse Inferencing Demo with IMU");

    if (!IMU.begin()) {
        Serial.println("Failed to initialize IMU!");
        while (1);
    }

    Serial.println("IMU initialized.");
//
//
//
//    BLE.setLocalName("Nano33BLE");
//    BLE.setAdvertisedService(shotService);
//
//      // add characteristics
//      shotService.addCharacteristic(inferenceCharacteristic);
//    
//      // add service
//      BLE.addService(shotService);
//    
//          // start advertising
//    if (!BLE.begin()) {
//        Serial.println("Starting BLE failed!");
//        while (1);
//    }
//    
//    if (BLE.advertise()) {
//        Serial.println("Started advertising");
//    } else {
//        Serial.println("Advertising failed to start");
//    }
//    
//      Serial.println("Bluetooth device active, waiting for connections...");
}

/**
 * @brief      Arduino main function
 */
void loop(){
//{
//    BLEDevice central = BLE.central();
//    if (central) {
//        
        ei_printf("Edge Impulse standalone inferencing (Arduino)\n");
        const size_t samples_per_inference = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE / 6; // Assuming 3-axis accel and gyro, adjust as necessary

        Serial.print("Connected to central: ");
//        Serial.println(central.address());
    
//        while (central.connected()) {
          for (size_t i = 0; i < samples_per_inference; i++) {
            float ax, ay, az, gx, gy, gz;
    
            // Wait for a new set of data
            while (!IMU.accelerationAvailable() || !IMU.gyroscopeAvailable());
    
            // Read acceleration and gyroscope
            IMU.readAcceleration(ax, ay, az);
            IMU.readGyroscope(gx, gy, gz);
    
            // Store in features array
            features[i * 6 + 0] = ax;
            features[i * 6 + 1] = ay;
            features[i * 6 + 2] = az;
            features[i * 6 + 3] = gx;
            features[i * 6 + 4] = gy;
            features[i * 6 + 5] = gz;
    
            delay(10);
        }

    
        if (sizeof(features) / sizeof(float) != EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {
            ei_printf("The size of your 'features' array is not correct. Expected %lu items, but had %lu\n",
                EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, sizeof(features) / sizeof(float));
            delay(1000);
            return;
        }

        ei_impulse_result_t result = { 0 };
    
        // the features are stored into flash, and we don't want to load everything into RAM
        signal_t features_signal;
        features_signal.total_length = sizeof(features) / sizeof(features[0]);
        features_signal.get_data = &raw_feature_get_data;
    
        // invoke the impulse
        EI_IMPULSE_ERROR res = run_classifier(&features_signal, &result, false /* debug */);
        if (res != EI_IMPULSE_OK) {
            ei_printf("ERR: Failed to run classifier (%d)\n", res);
            return;
        }
    
        // print inference return code
        ei_printf("run_classifier returned: %d\r\n", res);
        print_inference_result(result);
//        delay(1000);
}


void print_inference_result(ei_impulse_result_t result) {
    char data[256];  // Buffer to hold the output string
    char temp[64];  // Temporary string for individual results

    // Format timing information and prediction results
    snprintf(data, sizeof(data),
        "Timing: DSP %d ms, inference %d ms, anomaly %d ms\n",
        result.timing.dsp,
        result.timing.classification,
        result.timing.anomaly);

    // Append object detection or classification results
#if EI_CLASSIFIER_OBJECT_DETECTION == 1
    for (uint32_t i = 0; i < result.bounding_boxes_count; i++) {
        ei_impulse_result_bounding_box_t bb = result.bounding_boxes[i];
        if (bb.value != 0) {
            snprintf(temp, sizeof(temp), "%s (%f) [x: %u, y: %u, width: %u, height: %u]\n",
                     bb.label, bb.value, bb.x, bb.y, bb.width, bb.height);
            strncat(data, temp, sizeof(data) - strlen(data) - 1);  // Safely append
        }
    }
#else
    for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
        snprintf(temp, sizeof(temp), "%s: %.5f\n",
                 ei_classifier_inferencing_categories[i],
                 result.classification[i].value);
        strncat(data, temp, sizeof(data) - strlen(data) - 1);  // Safely append
    }
#endif

    // Append anomaly result if present
#if EI_CLASSIFIER_HAS_ANOMALY == 1
    snprintf(temp, sizeof(temp), "Anomaly: %.3f\n", result.anomaly);
    strncat(data, temp, sizeof(data) - strlen(data) - 1);
#endif

    // Send the formatted string over BLE
//    inferenceCharacteristic.setValue(data);
    Serial.println(data);  // Also print the data to the serial monitor for debugging
}
