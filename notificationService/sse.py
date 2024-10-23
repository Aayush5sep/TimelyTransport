import asyncio
from typing import Dict
import json

class SSEManager:
    def __init__(self):
        # Mapping of (user_id, user_type) to asyncio.Queue
        self.clients: Dict[str, Dict[str, asyncio.Queue]] = {}

    async def connect(self, user_id: str, user_type: str) -> asyncio.Queue:
        """Create a new connection for a specific user identified by user_id and user_type."""
        key = f"{user_id}:{user_type}"  # Create a unique key for the client
        queue = asyncio.Queue()
        self.clients[key] = queue
        return queue

    def disconnect(self, user_id: str, user_type: str):
        """Remove a disconnected client."""
        key = f"{user_id}:{user_type}"
        if key in self.clients:
            del self.clients[key]

    async def broadcast(self, user_id: str, user_type: str, message: str, status: str = "success", params: dict = {}):
        """Send a message along with its status to a specific client."""
        key = f"{user_id}:{user_type}"
        if key in self.clients:
            try:
                # Encode the message and status into a JSON object
                data = json.dumps({"message": message, "status": status, "params": params})
                await self.clients[key].put(data)
            except Exception as e:
                # Log or handle the error
                print(f"Failed to send message to {key}: {e}")


    async def event_generator(self, queue: asyncio.Queue):
        """Generator function to stream events to the client."""
        try:
            while True:
                message = await queue.get()
                yield f"data: {message}\n\n"
        except asyncio.CancelledError as err:
            pass  # Handle client disconnection
        except Exception as e:
            raise e