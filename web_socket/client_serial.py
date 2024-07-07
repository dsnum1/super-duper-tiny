import asyncio
import websockets


async def client_request():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = "Please show me the RGB value"
        await websocket.send(message)
        print(f'Client sent{message}')

        greeting = await websocket.recv()
        print(f'Client received {greeting}')



if __name__ == "__main__":
    # Create and run the event loop
    asyncio.run(client_request())

