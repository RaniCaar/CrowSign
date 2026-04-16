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
    flask_app.config['SECRET_KEY'] = 'crowsign-secret-pass'
    
    # Configurar SQL Server SQLite por ahora en caso de no tener conexion lista
    # Idealmente se cambiará por la cadena de conexión de SQL Server: 
    # 'mssql+pyodbc://user:pass@server/database?driver=ODBC+Driver+17+for+SQL+Server'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crowsign.db'
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
