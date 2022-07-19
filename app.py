import asyncio
from websockets import server

async def echo(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        websocket.id

        print("Hello")
        websocket.
        await websocket.send(message)

async def main():
    async with server.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
