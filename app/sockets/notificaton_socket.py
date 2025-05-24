from flask_socketio import join_room,emit

from app.extensions.socketio import socketio
from app.models.notifiaction_model import Notification

    
@socketio.on("join_room")
def on_join(data):
    user_id = data.get("user_id")
    room = f"user_{user_id}"
    join_room(room)
    print(f"🔗 Usuario {user_id} unido a sala {room}")



@socketio.on("send_notification")
def send_notification(data):
    to_user_id = data.get("to_user_id")
    message = data.get("message")
    room = f"user_{to_user_id}"
    print(f"📤 Enviando notificación a {room}: {message}")
    emit("notification", {"message": message}, room=room)
        