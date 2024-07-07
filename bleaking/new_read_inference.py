import asyncio
from bleak import BleakScanner, BleakClient, BleakError

DEVICE_NAME = "Nano33BLE"  # The advertised name of the BLE device
INFERENCE_UUID = "2a58"  # Replace with the actual UUID for inference data characteristic

async def connect_to_device(device_name):
    """Attempt to connect to a device by its name."""
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == device_name, timeout=20.0)
    if not device:
        raise BleakError(f"No device found with name {device_name}.")
    return device

def handle_inference_notification(sender, data):
    """Handle the notification from BLE characteristic."""
    print(f"Notification from {sender}: {data}")

async def monitor_device(device):
    """Manage connection to the device and subscribe to notifications."""
    async with BleakClient(device, timeout=30) as client:  # Increase the timeout to 30 seconds
        if not await client.is_connected():
            print(f"Failed to connect to {device.address}")
            return

        print(f"Connected to {device.name} at address {device.address}")

        # Discover services and characteristics
        services = await client.get_services()
        print("Discovered services and characteristics:")
        for service in services:
            print(f"[Service] {service.uuid} ({service.description})")
            for char in service.characteristics:
                if char.uuid == INFERENCE_UUID:
                    await client.start_notify(char.uuid, handle_inference_notification)
                    print(f"Subscribed to {char.uuid} for notifications.")

        # Keep the script running to continuously receive data
        try:
            while True:
                await asyncio.sleep(30)  # Adjust timing as needed for your application
        except asyncio.CancelledError:
            # Handle the cancellation gracefully
            print("Stopping notifications and disconnecting...")
        finally:
            if client.is_connected():
                await client.stop_notify(INFERENCE_UUID)
                print("Unsubscribed from notifications.")

import traceback

async def main():
    try:
        await BleakScanner.discover()  # Optional: Discover devices to make sure scanner works
        device = await connect_to_device(DEVICE_NAME)
        await monitor_device(device)
    except BleakError as e:
        print(f"BLE error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()  # Print the traceback to get more details about the error
# Run the main function in the asyncio event loop
asyncio.run(main())
