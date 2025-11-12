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
        access_payload = {
            "user_id": user.id,
            "username": user.username,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        access_token = jwt.encode(access_payload, "secret", algorithm="HS256")

        refresh_payload = {
            "user_id": user.id,
            "username": user.username,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        refresh_token = jwt.encode(refresh_payload, "secret", algorithm="HS256")

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.username,
        }
    else:
        return {"error": "Invalid credentials", "code": -32000}
    

async def handle_refresh_token(params):
    refresh_token = params.get("refresh_token")
    if not refresh_token:
        return {"error": "Refresh token required"}

    try:
        decoded = jwt.decode(refresh_token, "secret", algorithms=["HS256"])

        # Ensure token type is refresh
        if decoded.get("type") != "refresh":
            return {"error": "Invalid token type"}

        user_id = decoded.get("user_id")
        username = decoded.get("username")

        # (Optional) verify user still exists or is active
        user = User.query.filter_by(id=user_id, username=username).first()
        if not user:
            return {"error": "User not found"}

        # Generate a new access token
        new_access_payload = {
            "user_id": user.id,
            "username": user.username,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60)
        }
        new_access_token = jwt.encode(new_access_payload, "secret", algorithm="HS256")

        return {
            "message": "New access token issued",
            "access_token": new_access_token
        }

    except jwt.ExpiredSignatureError:
        return {"error": "Refresh token expired, please log in again"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid refresh token"}


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
