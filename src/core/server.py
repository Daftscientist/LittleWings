import json
import time
import asyncio
from core.server import Server

class WebsocketView():
    async def execute_command(self, server: Server, command):
        server.execute_command(command)

    async def stream_docker_logs(self, ws, server: Server):
        """
        Stream logs from the Docker container and send them over the WebSocket connection.
        """
        logs = server.stream_terminal_logs()
        async for line in logs:
            await ws.send(json.dumps({"type": "log", "data": line.decode("utf-8")}))

    async def entry(self, request, ws):
        heartbeat_ending_at = time.time() + 60 * 3
        server = None

        async def send_heartbeat():
            nonlocal heartbeat_ending_at
            while heartbeat_ending_at > time.time():
                await asyncio.sleep(1)

        async def handle_messages():
            nonlocal heartbeat_ending_at, server
            while heartbeat_ending_at > time.time():
                try:
                    data = await ws.recv()
                    data = json.loads(data)

                    if data.get("type").lower() == "connect":
                        server = Server(container_id=data.get("server_id"))
                        server.load_from_docker()
                        await ws.send(json.dumps({"status": "success", "message": "Server connected"}))
                        asyncio.create_task(self.stream_docker_logs(ws, server))

                    elif data.get("type").lower() == "command":
                        if server:
                            await self.execute_command(server, data["command"])
                        else:
                            await ws.send(json.dumps({"status": "error", "message": "Server not connected"}))

                    elif data.get("type").lower() == "heartbeat":
                        heartbeat_ending_at = time.time() + 60 * 3
                        await ws.send(json.dumps({"status": "success", "message": "Heartbeat renewed"}))
                    
                    else:
                        await ws.send(json.dumps({"status": "error", "message": "Invalid request"}))

                except Exception as e:
                    print(f"Error: {e}")
                    break

        await asyncio.gather(send_heartbeat(), handle_messages())
