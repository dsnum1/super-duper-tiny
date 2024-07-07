import asyncio
import websockets
import serial
import time


async def forward_to_clients(websocket):
    incoming_request = await websocket.recv()
    print(f' Received following request: {incoming_request}')
    with serial.Serial('COM12', 9600, timeout=1) as ser:
        while True:
            message = ser.read_until(b'\n')
            await websocket.send(message)


async def main():
    async with websockets.serve(forward_to_clients, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())



#     while True:
#         message = arduino.readline().decode('utf-8').strip()
#         if message:
#             print(f"Sending message to WebSocket clients: {message}")
#             await websocket.send(message)

# async def main():
#     # Setup the WebSocket server
#     async with websockets.serve(forward_to_clients, "localhost", 5678):
#         await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     # Create and run the event loop
#     asyncio.run(main())
