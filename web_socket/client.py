import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        name = input("What is your name? ")
        await websocket.send(name)
        print(f'Client sent {name}')

        greeting = await websocket.recv()
        print(f'Client received {greeting}')



if __name__ == "__main__":
    # Create and run the event loop
    asyncio.run(hello())
