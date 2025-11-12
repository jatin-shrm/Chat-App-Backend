import json
from flaskr.routes.events import handle_register, handle_login,handle_refresh_token, get_user_details



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

async def handle_ws_message(ws, message):
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

    try:
        if method == "register":
            result = await handle_register(params)
        elif method == "login":
            result = await handle_login(params)

        elif method == "refresh_token":
            result = await handle_refresh_token(params)

        elif method == "get_user_details":
            result = await get_user_details(params)
        else:
            await send_error(ws, req_id, f"Unknown method '{method}'", code=-32601)
            return

        if isinstance(result, dict) and "error" in result:
                await send_error(ws, req_id, result["error"])
        else:
            await send_result(ws, req_id, result)
    except Exception as e:
        await send_error(ws, req_id, f"Internal error: {str(e)}", code=-32603)