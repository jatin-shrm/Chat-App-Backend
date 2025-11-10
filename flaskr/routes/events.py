import json
import jwt
from datetime import datetime, timedelta, timezone
from flaskr.models import User
from flaskr.extensions import db


async def handle_register(params):
    username = params.get("username")
    email = params.get("email")
    password = params.get("password")

    if not username or not email or not password:
        return {"error": "All fields required", "code": -32602}

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return {"error": "Username or email already exists", "code": -32602}    

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return {
        "message": "Registration successful",
        "username": new_user.username,
    }


async def handle_login(params):
    username = params.get("username")
    password = params.get("password")

    if not username or not password:
        return {"error": "Username and password required"}

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")

        return {
            "message": "Login successful",
            "token": token,
            "user" : user.username,
        }
    else:
        return {"error": "Invalid credentials", "code": -32000}

async def get_user_details(params):
    token = params.get("token")
    if not token:
        return {"error": "Missing token"}

    try:
        decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

    user = User.query.get(decoded["user_id"])
    if not user:
        return {"error": "User not found"}

    return {
        "message": "User details fetched",
        "username": user.username,
    }
