
class WebsocketView():
    path = "/api/ws"

    async def entry(self, request, ws):
        while True:
            data = await ws.recv()
            print(data)
            await ws.send(data[::-1])
