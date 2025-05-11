from flask_socketio import emit


def register_socketio_events(socketio):
    
    @socketio.on("connect")
    def handle_new_connection():
        print("un usuario se conecto ")
    
    @socketio.on("disconnect")
    def handle_disconnect():
        print("un usuario se desconecto")
    