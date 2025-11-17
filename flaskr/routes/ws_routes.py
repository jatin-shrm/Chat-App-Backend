import json
from flaskr.models import User
from flaskr.routes.events import (
    handle_register,
    handle_login,
    handle_refresh_token,
    handle_auth_with_token,
    get_user_details,
    get_all_users,
    handle_upload_profile_picture,
    get_profile_picture
)


async def send_result(ws, request_id, result):
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }))


async def send_error(ws, request_id, message, code=-32603):
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }))

def _get_session(client_sessions, ws):
    if ws not in client_sessions:
        client_sessions[ws] = {"user_id": None, "access_token": None}
    return client_sessions[ws]


def _get_session_user(session):
    user_id = session.get("user_id") if session else None
    if not user_id:
        return None
    return User.query.get(user_id)


async def handle_ws_message(ws, message, client_sessions):
    session = _get_session(client_sessions, ws)
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        await send_error(ws, None, "Invalid JSON")
        return

    if data.get("jsonrpc") != "2.0":
        await send_error(ws, data.get("id"), "Invalid JSON-RPC version")
        return
    

    if "id" not in data or data["id"] is None or data["id"] == "":
        await send_error(ws, None, "Missing 'id' in request")
        return

    method = data.get("method")
    params = data.get("params", {})
    req_id = data.get("id")
    token = data.get("access_token")

    # Fall back to stored token if client omits it
    if not token:
        token = session.get("access_token")

    current_user = _get_session_user(session)

    try:
        if method == "register":
            result = await handle_register(params)
        elif method == "login":
            result = await handle_login(params)
            if isinstance(result, dict) and "error" not in result:
                session["access_token"] = result.get("access_token")
                session["user_id"] = result.get("user_id")

        elif method == "refresh_token":
            result = await handle_refresh_token(params)
            if isinstance(result, dict) and "error" not in result:
                session["access_token"] = result.get("access_token")
                session["user_id"] = result.get("user_id", session.get("user_id"))

        elif method == "auth_with_token":
            result = await handle_auth_with_token(params)
            if isinstance(result, dict) and "error" not in result:
                session["user_id"] = result.get("user_id")
                session["access_token"] = params.get("access_token") or token

        elif method == "get_user_details":
            result = await get_user_details(params, token=token, current_user=current_user)
        elif method == "get_all_users":
            result = await get_all_users(params, token=token, current_user=current_user)
        elif method == "upload_profile_picture":
            result = await handle_upload_profile_picture(params, token=token, current_user=current_user)
        elif method == "get_profile_picture":
            result = await get_profile_picture(params, token=token, current_user=current_user)
        else:
            await send_error(ws, req_id, f"Unknown method '{method}'", code=-32601)
            return

        if isinstance(result, dict) and "error" in result:
            await send_error(ws, req_id, result["error"])
        else:
            await send_result(ws, req_id, result)
    except Exception as e:
        await send_error(ws, req_id, f"Internal error: {str(e)}", code=-32603)