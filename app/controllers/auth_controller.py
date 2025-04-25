from flask_jwt_extended import create_access_token
from models.user_models import User

class AuthController:
    @staticmethod
    def register(username, email, password, bio='', profile_pic_url=''):
        """Registra un nuevo usuario"""
        # Validaciones
        if not username or not email or not password:
            return {"error": "Todos los campos son requeridos"}, 400
            
        # Verificar si el usuario ya existe
        if User.find_by_username(username):
            return {"error": "Nombre de usuario ya existe"}, 400
            
        if User.find_by_email(email):
            return {"error": "Email ya está registrado"}, 400
            
        try:
            user_id = User.create(username, email, password, bio, profile_pic_url)
            return {"message": "Usuario registrado correctamente", "user_id": user_id}, 201
        except Exception as e:
            return {"error": str(e)}, 500
    
    @staticmethod
    def login(username, password):
        """Inicia sesión de un usuario"""
        if not username or not password:
            return {"error": "Usuario y contraseña son requeridos"}, 400
            
        user = User.find_by_username(username)
        
        if not user or not User.check_password(user, password):
            return {"error": "Usuario o contraseña incorrectos"}, 401
            
        access_token = create_access_token(identity=str(user['_id']))
        
        return {
            "message": "Login exitoso",
            "token": access_token,
            "user_id": str(user['_id']),
            "username": user['username']
        }, 200
