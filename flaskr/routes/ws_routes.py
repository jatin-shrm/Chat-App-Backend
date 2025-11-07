from flaskr.models import User
from flask_socketio import emit
from flaskr.extensions import db

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


    @socketio.on('register')
    def handle_register(data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            emit('response', {'status': 'error', 'message': 'All fields required'})
            return
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            emit('response', {'status': 'error', 'message': 'Username or email already exists'})
            return
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        emit('response', {'status': 'success', 'message': 'Registration successful'})


    @socketio.on('login')
    def handle_login(data):
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            emit('response', {'status': 'success', 'message': 'Login successful'})
        else:
            emit('response', {'status': 'error', 'message': 'Invalid credentials'})

    @socketio.on('connect')
    def handle_connect():
        print("A client connected")

    @socketio.on('message')
    def handle_message(msg):
        print("Received:", msg)
        socketio.emit('response', {'message': f"Server got your message: {msg}"})

    @socketio.on('disconnect')
    def handle_disconnect():
        print("A client disconnected")
