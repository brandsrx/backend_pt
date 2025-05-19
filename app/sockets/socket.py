from flask_socketio import SocketIO, send, emit
from flask import request

def register_socketio_events(socketio: SocketIO):
    @socketio.on('connect')
    def handle_connect():
        emit('message', {"user_id":request.sid})

    @socketio.on('message')
    def handle_message(msg):
        print(f'📨 Mensaje recibido: {msg}')
        send(msg, broadcast=True)
