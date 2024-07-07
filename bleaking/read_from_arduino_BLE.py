import asyncio
import struct
import pandas as pd
import matplotlib.pyplot as plt
from bleak import BleakScanner, BleakClient, BleakError


DEVICE_NAME = "Nano33BLE"  # The advertised name of the BLE device
ACCELERATION_UUID = "2a58"  # Replace with your acceleration characteristic UUID
GYROSCOPE_UUID = "2a59"  # Replace with your gyroscope characteristic UUID
COMMAND_UUID = "2a60"


# Initialize lists to store the data
indexes = []
ax_values, ay_values, az_values = [], [], []
gx_values, gy_values, gz_values = [], [], []


async def send_start_command(client, command_uuid):
    # command_uuid = "2a60"  # UUID for the command characteristic, matching the Arduino setup
    try:
        print("Sending start command to the device...")
        await client.write_gatt_char(command_uuid, bytearray("start", "utf-8"))
        print("Start command sent.")
    except Exception as e:
        print(f"Failed to send start command: {e}")

def handle_acceleration_notification(sender, data):
    index, ax, ay, az = struct.unpack('>h3f', data)
    print(f"Sample {index}: ax={ax}, ay={ay}, az={az}")
    indexes.append(index)
    ax_values.append(ax)
    ay_values.append(ay)
    az_values.append(az)

def handle_gyroscope_notification(sender, data):
    # Assuming data format is: index, gx, gy, gz (index is reused, not stored again)
    index, gx, gy, gz = struct.unpack('>h3f', data)
    print(f"Sample {index}: gx={gx}, gy={gy}, gz={gz}")
    gx_values.append(gx)
    gy_values.append(gy)
    gz_values.append(gz)


async def list_all_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover(timeout=5.0)
    for device in devices:
        print(device.metadata)
        print(f"Device Name: {device.name}, Device Address: {device.address}")
    print("Scan complete.\n")

async def connect_to_device(device_name):
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == device_name, timeout=10.0)
    if not device:
        raise BleakError(f"No device found with name {device_name}.")
    return device

async def read_data_from_device(device):
    try:
        async with BleakClient(device) as client:
            print(f"Connected to {device.name}")
            services = await client.get_services()
            
            print(services.characteristics.keys())
            for char in services.characteristics.values():
                print(char.uuid, char.service_uuid)
                if char.uuid.find(ACCELERATION_UUID)!=-1:
                    acceleration_uuid_found =    char.uuid 
                    
                elif char.uuid.find(GYROSCOPE_UUID)!=-1:
                    gyroscope_uuid_found = char.uuid

                elif char.uuid.find(COMMAND_UUID)!=-1:
                    command_uuid_found = char.uuid

            
            await client.start_notify(acceleration_uuid_found, handle_acceleration_notification)
            print("Subscribed to acceleration notifications.")
            # print("Acceleration characteristic UUID not found.")

            await client.start_notify(gyroscope_uuid_found, handle_gyroscope_notification)
            print("Subscribed to gyroscope notifications.")
            await send_start_command(client, command_uuid_found)
            # print("Gyroscope characteristic UUID not found.")

            # Keep the script alive to continue receiving notifications
            print("Receiving data for 20 seconds...")
            await asyncio.sleep(10)

            # Optionally, stop notifications if no longer needed
            await client.stop_notify(acceleration_uuid_found)
            await client.stop_notify(gyroscope_uuid_found)


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

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(indexes, ax_values, label='Ax')
    plt.plot(indexes, ay_values, label='Ay')
    plt.plot(indexes, az_values, label='Az')
    plt.title('Acceleration Data')
    plt.xlabel('Sample Index')
    plt.ylabel('Acceleration')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(indexes, gx_values, label='Gx')
    plt.plot(indexes, gy_values, label='Gy')
    plt.plot(indexes, gz_values, label='Gz')
    plt.title('Gyroscope Data')
    plt.xlabel('Sample Index')
    plt.ylabel('Gyroscope')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Saving to Excel
    df = pd.DataFrame({
        'ax': ax_values,
        'ay': ay_values,
        'az': az_values,
        'gx': gx_values,
        'gy': gy_values,
        'gz': gz_values
    })
    df.to_excel('imu_data.xlsx', index=False)
    print("Data saved to imu_data.xlsx")

# Run the main function
asyncio.run(main())
