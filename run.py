import asyncio
import threading
from flaskr import create_app
from flaskr.routes.handlers import start_websocket_server

app = create_app()

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def run_websocket():
    asyncio.run(start_websocket_server())

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_websocket()
