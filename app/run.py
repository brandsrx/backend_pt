from flask import Flask,jsonify
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

from app.extensions.socketio import socketio
from app.extensions.redis_extencion import init_extensions
from app.sockets.socket import register_socketio_events
import os

def create_app():
    app = Flask(__name__,static_folder='static',static_url_path='/static')
    app.config.from_object(Config)


    jwt = JWTManager(app)
    CORS(app)

    # Inicializar base de datos
    init_db()
    
    # Iniciamos los sockets
    socketio.init_app(app)
    register_socketio_events(socketio)
    init_extensions(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(notification_bp,url_prefix='/api/notification')
    
    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
