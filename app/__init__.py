import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    # Establecer la ubicación estática y de plantillas
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    flask_app = Flask(__name__, template_folder=frontend_dir, static_folder=static_dir)
    flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'crowsign-dev-secret')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance', 'crowsign.db')
    )
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(flask_app)
    db.init_app(flask_app)
    socketio.init_app(flask_app)

    from app.controllers.auth import auth_bp
    flask_app.register_blueprint(auth_bp)

    from app.controllers.main import main_bp
    flask_app.register_blueprint(main_bp)
    
    from app.controllers.api import api_bp
    flask_app.register_blueprint(api_bp)
    
    # Importar eventos de socketio para que se registren
    with flask_app.app_context():
        import app.controllers.socket

    # Crear tablas
    with flask_app.app_context():
        db.create_all()

    return flask_app
