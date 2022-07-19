import asyncio
from websockets import client
import websockets
from threading import Thread

def createClient(id):
    async def hello():
        async with client.connect("ws://localhost:8765") as websocket:
            while True:
                await websocket.send("Hello world!")
                try:
                    print(f"Thread: {id}")
                    message = await websocket.recv()
                    print(message)
                except client.ClientConnection.close_expected:
                    print(f'Terminated')
                    break
    asyncio.run(hello())

t1 = Thread(target=createClient, args=(1,))
t2 = Thread(target=createClient, args=(2,))

t1.start()
t2.start()

# t1.join()
# t2.join()
