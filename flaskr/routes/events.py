import json
import jwt
import datetime
from flaskr.models import User
from flaskr.extensions import db

async def handle_ws_message(ws, message):
    """
    Entry point for handling all WebSocket messages.
    """
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        await ws.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
        return

    method = data.get("method")
    params = data.get("params", {})

    if method == "register":
        await handle_register(ws, params)
    elif method == "login":
        await handle_login(ws, params)
    else:
        await ws.send(json.dumps({"status": "error", "message": "Unknown method"}))

async def handle_register(ws, data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        await ws.send(json.dumps({"status": "error", "message": "All fields required"}))
        return

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        await ws.send(json.dumps({"status": "error", "message": "Username or email already exists"}))
        return

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    await ws.send(json.dumps({"status": "success", "message": "Registration successful"}))

async def handle_login(ws, data):
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")
        await ws.send(json.dumps({
            "status": "success",
            "message": "Login successful",
            "token": token
        }))
    else:
        await ws.send(json.dumps({"status": "error", "message": "Invalid credentials"}))
