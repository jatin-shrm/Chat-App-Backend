import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate

def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)
    # socketio.init_app(app)

    # from .routes import api_routes
    # app.register_blueprint(routes.bp)

    from .routes import events,api_routes
    app.register_blueprint(api_routes.bp)
    # events.register_ws_events(socketio)

    return app