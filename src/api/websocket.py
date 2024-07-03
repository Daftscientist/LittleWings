import json
import time
import asyncio
from core.server import Server

HEARTBEAT_TIMEOUT = 60 * 3  # 3 minutes
HEARTBEAT_REMINDER_THRESHOLD = 15  # seconds before heartbeat ends to send reminder

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
        heartbeat_ending_at = time.time() + HEARTBEAT_TIMEOUT
        server = None
        reminder_sent = False  # flag to ensure reminder is sent only once

        async def send_heartbeat():
            nonlocal heartbeat_ending_at, reminder_sent

            while heartbeat_ending_at > time.time():
                # Check if within reminder threshold and reminder not yet sent
                if heartbeat_ending_at - time.time() <= HEARTBEAT_REMINDER_THRESHOLD and not reminder_sent:
                    await ws.send(json.dumps({"type": "heartbeat_reminder", "message": f"Heartbeat about to end in {HEARTBEAT_REMINDER_THRESHOLD}, please renew."}))
                    reminder_sent = True  # Set flag to true after sending reminder
                await asyncio.sleep(1)

        async def handle_messages():
            nonlocal heartbeat_ending_at, server, reminder_sent
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
                        heartbeat_ending_at = time.time() + HEARTBEAT_TIMEOUT
                        reminder_sent = False  # Reset reminder flag to allow reminder to be sent again
                        await ws.send(json.dumps({"status": "success", "message": "Heartbeat renewed"}))
                    
                    else:
                        await ws.send(json.dumps({"status": "error", "message": "Invalid request"}))

                except Exception as e:
                    raise e

        await asyncio.gather(send_heartbeat(), handle_messages())