# This is a simple websocket server to just get started with it


import asyncio
import websockets


async def hello(websocket):
    name =  await websocket.recv()
    print(f'Server received {name}!')
    greeting = f'Hello {name}!'
    await websocket.send(greeting)


async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    # Create and run the event loop
    asyncio.run(main())

