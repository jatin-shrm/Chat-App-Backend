import socketio
import time

# ----------------- Setup Socket.IO client -----------------
sio = socketio.Client(logger=True, engineio_logger=True)

# ----------------- Event Handlers -----------------

@sio.event
def connect():
    print("✅ Connected to server!")

@sio.event
def connect_error(data):
    print("❌ Failed to connect:", data)

@sio.event
def disconnect():
    print("⚡ Disconnected from server.")

# Generic response listener
@sio.on('response')
def on_response(data):
    print("📩 Server response:", data)

    # Automatically trigger login after successful registration
    if data.get('message') == 'Registration successful':
        time.sleep(1)  # small delay for DB commit
        login_user(direct=True)

# ----------------- Helper: unified emit -----------------

def emit_action(method, params):
    """Emit a generic action event (method + params)."""
    payload = {"method": method, "params": params}
    print(f"➡️  Emitting 'action' with method '{method}' ->", params)
    sio.emit("action", payload)


# ----------------- Test Functions -----------------

def register_user(direct=False):
    """Send registration request via direct or action method."""
    user_data = {
        "username": "testuser123",
        "email": "testuser1234@example.com",
        "password": "password123"
    }

    if direct:
        print("📝 Sending direct register event...")
        sio.emit("register", user_data)
    else:
        print("📝 Sending action(register)...")
        emit_action("register", user_data)


def login_user(direct=False):
    """Send login request via direct or action method."""
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }

    if direct:
        print("🔑 Sending direct login event...")
        sio.emit("login", login_data)
    else:
        print("🔑 Sending action(login)...")
        emit_action("login", login_data)


# ----------------- Main -----------------

if __name__ == "__main__":
    try:
        # Connect to Flask-SocketIO server
        sio.connect("http://localhost:5000")
        print("🚀 Connected — starting tests...")

        # --- Choose how you want to test ---
        # Option 1: Use unified 'action' event
        register_user(direct=False)

        # Option 2: Use direct 'register' event
        # register_user(direct=True)

        # Keep the client alive to receive responses
        sio.wait()

    except KeyboardInterrupt:
        print("\n🛑 Client stopped manually.")
        sio.disconnect()
