from flask_socketio import SocketIO
from app.config import Config

socketio = SocketIO(cors_allowed_origins='*')
