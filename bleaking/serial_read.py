import serial
import time

# Configuration for the serial connection
serial_port = 'COM9'  # Update this to the port where your Arduino is connected
baud_rate = 921600  # Should match the baud rate set in your Arduino sketch

# Try to establish a serial connection
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connected to {serial_port} at {baud_rate} bps")
except Exception as e:
    print(f"Error: {e}")
    exit()

# Function to parse the inference results from the serial data
def parse_inference(data):
    results = {}
    lines = data.split('\n')
    for line in lines:
        if ":" in line:
            key, value = line.split(':', 1)
            results[key.strip()] = value.strip()
    return results

# Main loop to continuously read from the serial port and update dictionary
try:
    inference_results = {}
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8')
            if "Timing" in line or "Anomaly" in line or ":" in line:  # Filter relevant lines
                print(line)  # Optionally print the raw data for debugging
                updated_results = parse_inference(line)
                inference_results.update(updated_results)
                print(inference_results)  # Print updated dictionary
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting program")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    ser.close()  # Always close the serial connection gracefully

