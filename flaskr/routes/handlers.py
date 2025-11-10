import asyncio
import websockets
from flaskr import create_app
from flaskr.extensions import db
from flaskr.routes.ws_routes import handle_ws_message

connected_clients = set()

app = create_app()
app.app_context().push()

async def ws_handler(ws):
    connected_clients.add(ws)
    print("✅ Client connected")
    try:
        async for message in ws:
            print("Received:", message)
            await handle_ws_message(ws, message)
    except websockets.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        connected_clients.remove(ws)

async def start_websocket_server():
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("🚀 WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # Keep running forever
