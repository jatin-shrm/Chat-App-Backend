import json
import jwt
from datetime import datetime, timedelta, timezone
from flaskr.models import User
from flaskr.extensions import db
from functools import wraps


def requires_auth(func):
    @wraps(func)
    async def wrapper(params, token=None, current_user=None, *args, **kwargs):
        if current_user:
            kwargs["current_user"] = current_user
            return await func(params, *args, **kwargs)

        if not token:
            return {"error": "Access token required"}

        try:
            decoded = jwt.decode(token, "secret", algorithms=["HS256"])

            if decoded.get("type") != "access":
                return {"error": "Invalid token type"}

            user_id = decoded.get("user_id")
            user = User.query.get(user_id)

            if not user:
                return {"error": "User not found"}

            kwargs["current_user"] = user
            return await func(params, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return {"error": "Access token expired", "need_refresh": True}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}

    return wrapper


async def handle_register(params):
    name = params.get("name")
    username = params.get("username")
    email = params.get("email")
    password = params.get("password")

    if not name or not username or not email or not password:
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
        "name": new_user.name
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
            "user_id": user.id,
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

        if decoded.get("type") != "refresh":
            return {"error": "Invalid token type"}

        user_id = decoded.get("user_id")
        username = decoded.get("username")

        user = User.query.filter_by(id=user_id, username=username).first()
        if not user:
            return {"error": "User not found"}

        new_access_payload = {
            "user_id": user.id,
            "username": user.username,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60)
        }
        new_access_token = jwt.encode(new_access_payload, "secret", algorithm="HS256")

        return {
            "message": "New access token issued",
            "access_token": new_access_token,
            "user_id": user.id,
            "username": user.username,
        }

    except jwt.ExpiredSignatureError:
        return {"error": "Refresh token expired, please log in again"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid refresh token"}


async def handle_auth_with_token(params):
    token = params.get("access_token")
    if not token:
        return {"error": "Access token required"}

    try:
        decoded = jwt.decode(token, "secret", algorithms=["HS256"])
        if decoded.get("type") != "access":
            return {"error": "Invalid token type"}

        user_id = decoded.get("user_id")
        username = decoded.get("username")

        user = User.query.filter_by(id=user_id, username=username).first()
        if not user:
            return {"error": "User not found"}

        return {
            "message": "Authenticated successfully",
            "user_id": user.id,
            "username": user.username,
        }

    except jwt.ExpiredSignatureError:
        return {"error": "Access token expired", "need_refresh": True}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}



@requires_auth
async def get_user_details(params, current_user=None):
    return {
        "message": "User details fetched",
        "username": current_user.username,
        "email": current_user.email,
    }


@requires_auth
async def get_all_users(params, current_user=None):
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "name": user.name, "email": user.email} for user in users]
    return {
        "message": "All users fetched",
        "users": user_list,
        
    }

@requires_auth
async def handle_upload_profile_picture(params, current_user=None):
    image_url = params.get("image_url")

    if not image_url:
        return {"error": "Image URL required"}

    # Update user profile image
    current_user.profile_image = image_url
    db.session.commit()

    return {
        "message": "Profile picture updated successfully",
        "profile_image": current_user.profile_image,
        "user_id": current_user.id,
        "username": current_user.username
    }

@requires_auth
async def get_profile_picture(params, current_user=None):
    if not current_user.profile_image:
        return {
            "message": "No profile picture found",
            "profile_image": None
        }

    return {
        "message": "Profile picture fetched successfully",
        "user_id": current_user.id,
        "profile_image": current_user.profile_image
    }
