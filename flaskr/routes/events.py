from flask_socketio import emit
from flaskr.routes.handlers import handle_register, handle_login

def register_ws_events(socketio):
    @socketio.on('action')
    def handle_action(data):
        method = data.get('method')
        params = data.get('params', {})

        if method == "register":
            handle_register(params)
        elif method == "login":
            handle_login(params)
        else:
            emit('response', {'status': 'error', 'message': 'Unknown method'})

    @socketio.on('connect')
    def handle_connect():
        print("A client connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        print("A client disconnected")
