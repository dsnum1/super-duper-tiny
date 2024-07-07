import asyncio
import struct
import pandas as pd
import matplotlib.pyplot as plt
from bleak import BleakScanner, BleakClient, BleakError

DEVICE_NAME = "Nano33BLE"  # The advertised name of the BLE device
COMMAND_UUID = "2a60"  # UUID for sending commands
ACCELERATION_UUID = "2a58"  # UUID for reading acceleration data
GYROSCOPE_UUID = "2a59"  # UUID for reading gyroscope data



async def list_all_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover(timeout=5.0)
    for device in devices:
        print(device.metadata)
        print(f"Device Name: {device.name}, Device Address: {device.address}")
    print("Scan complete.\n")


async def request_and_read_data(client, command_uuid, data_uuid, data_handler, i):
    # Send a request for data
    print(i)
    await client.write_gatt_char(command_uuid, bytearray("GET_SAMPLE:{i}", "utf-8"))
    # Wait for the Arduino to process the command and write the data
    await asyncio.sleep(0.1)  # Adjust based on the Arduino's processing time
    
    # Read the data
    data = await client.read_gatt_char(data_uuid)
    data_handler(data)

def handle_acceleration_data(data):
    # Example data handling function
    # Unpack the data and append to your data lists
    index, ax, ay, az, gx, gy, gz = struct.unpack('>H6f', data)

    # Print the unpacked data
    print(f"Sample Index: {index}")
    print(f"Accelerometer: X={ax}, Y={ay}, Z={az}")
    print(f"Gyroscope: X={gx}, Y={gy}, Z={gz}")
    print("Handling acceleration data...")

def handle_gyroscope_data(data):
    # Example data handling function
    # Unpack the data and append to your data lists
    print("Handling gyroscope data...")

async def read_data_from_device(device):
    try:
        async with BleakClient(device) as client:
            services = await client.get_services()

            print(f"Connected to {device.name}")
            for char in services.characteristics.values():
                print(char.uuid, char.service_uuid)
                if char.uuid.find(ACCELERATION_UUID)!=-1:
                    acceleration_uuid_found =    char.uuid 
                    
                # elif char.uuid.find(GYROSCOPE_UUID)!=-1:
                #     gyroscope_uuid_found = char.uuid

                elif char.uuid.find(COMMAND_UUID)!=-1:
                    command_uuid_found = char.uuid

            # Main loop to request and read data
            for i in range(200):  # Example: request 20 data samples
                await request_and_read_data(client, command_uuid_found, acceleration_uuid_found, handle_acceleration_data, i)
                # await request_and_read_data(client, command_uuid_found, gyroscope_uuid_found, handle_gyroscope_data)
                await asyncio.sleep(0.2)  # Interval between data requests
                
            # After collecting data, proceed to plotting and saving...

    except Exception as e:
        print(e)
        print(f"Disconnected from {device.name}")

async def connect_to_device(device_name):
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == device_name, timeout=10.0)
    if not device:
        raise BleakError(f"No device found with name {device_name}.")
    return device

async def main():
    await list_all_devices()  # List all available Bluetooth devices

    try:
        device = await connect_to_device(DEVICE_NAME)
        print(f"Device {device.name} found with address {device.address}")
        await read_data_from_device(device)
    except BleakError as e:
        print(e)
    await asyncio.sleep(20)  # Adjust based on your expected data collection duration


# Run the main function
asyncio.run(main())
