from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from flask_socketio import SocketIO

from app.config import Config
from app.database import init_db

from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.controllers.post_controller import post_bp
from app.controllers.notification_controller import notification_bp

from app.extensions import socketio
from app.sockets.socket import register_socketio_events

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    jwt = JWTManager(app)
    CORS(app)

    # Inicializar base de datos
    init_db()
    
    # Iniciamos los sockets
    socketio.init_app(app)
    register_socketio_events(socketio)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(notification_bp,url_prefix='/api/notification')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
