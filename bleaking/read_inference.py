import asyncio
import struct
import pandas as pd
import matplotlib.pyplot as plt
from bleak import BleakScanner, BleakClient, BleakError


DEVICE_NAME = "Nano33BLE"  # The advertised name of the BLE device
INFERENCE_UUID = "2a58"  # Replace with your acceleration characteristic UUID
COMMAND_UUID = "2a60"


# Initialize lists to store the data

async def send_start_command(client, command_uuid):
    # command_uuid = "2a60"  # UUID for the command characteristic, matching the Arduino setup
    try:
        print("Sending start command to the device...")
        await client.write_gatt_char(command_uuid, bytearray("start", "utf-8"))
        print("Start command sent.")
    except Exception as e:
        print(f"Failed to send start command: {e}")

def handle_inference_notification(sender, data):
    # index, ax, ay, az = struct.unpack('>h3f', data)
    # print(f"Sample {index}: ax={ax}, ay={ay}, az={az}")

    print(data)


async def list_all_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover(timeout=20.0)
    for device in devices:
        print(device.metadata)
        print(f"Device Name: {device.name}, Device Address: {device.address}")
        a = [bytes_to_hex_string(found_data) for found_data in device.metadata['manufacturer_data'].values()]
        # print(f"Manufacturer Data: {a}" )
    print("Scan complete.\n")

async def connect_to_device(device_name):
    # device = await BleakScanner.find_device_by_address(device_identifier="F4:49:02:9F:FA:CE", timeout=10)
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == device_name, timeout=20.0)
    if not device:
        raise BleakError(f"No device found with name {device_name}.")
    return device


def bytes_to_hex_string(byte_data):
    return ' '.join(f'{byte:02X}' for byte in byte_data)

async def read_data_from_device(device):
    try:
        async with BleakClient(device) as client:
            print(f"Connected to {device.name}")
            services = await client.get_services()
            
            print(services.characteristics.keys())
            for char in services.characteristics.values():
                print(char.uuid, char.service_uuid)
                if char.uuid.find(INFERENCE_UUID)!=-1:
                    inference_uuid_found =    char.uuid 

            
            await client.start_notify(inference_uuid_found, handle_inference_notification)
            print("Subscribed to inference notifications.")
            # print("Acceleration characteristic UUID not found.")

            # await client.start_notify(gyroscope_uuid_found, handle_gyroscope_notification)
            # print("Subscribed to gyroscope notifications.")
            # await send_start_command(client, command_uuid_found)
            # print("Gyroscope characteristic UUID not found.")

            # Keep the script alive to continue receiving notifications
            print("Receiving data for 20 seconds...")
            await asyncio.sleep(10)

            # Optionally, stop notifications if no longer needed
            await client.stop_notify(inference_uuid_found)


    except Exception as e:
        print(e)
        print(f"Disconnected from {device.name}")

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
