import re
import warnings
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio

from sqs import SQSManager
from sse import SSEManager
from config import settings
from dependencies import validate_token

# Ignore Deprecation Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

sqs_manager = SQSManager()
sse_manager = SSEManager()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    print("Starting application...")
    receive_task = asyncio.create_task(
        sqs_manager.receive_messages(sse_manager.broadcast)
    )

    try:
        yield  # Keep the app running within this context
    finally:
        print("Shutting down the application...")
        receive_task.cancel()
        try:
            await receive_task
        except asyncio.CancelledError:
            print("SQS message listener task cancelled.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/notification-stream")
async def stream(request: Request, token: str):
    """Endpoint to establish an SSE connection for a specific user."""
    user_details = validate_token(token)
    user_id = user_details.get("user_id")
    user_type = user_details.get("user")
    queue = await sse_manager.connect(user_id, user_type)

    async def disconnect_handler():
        sse_manager.disconnect(user_id, user_type)

    # Clean connection on client disconnect
    request.state.background = BackgroundTasks()
    request.state.background.add_task(disconnect_handler)

    return StreamingResponse(
        sse_manager.event_generator(queue),
        media_type="text/event-stream"
    )


@app.post("/manual-notify")
async def notify_client(message: str, user_details: dict = Depends(validate_token)):
    """API to send a notification to all connected clients."""
    user_id = user_details.get("user_id")
    user_type = user_details.get("user")
    await sse_manager.broadcast(message, user_id, user_type)
    return {"message": "Notification sent"}