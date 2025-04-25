from models.follow_models import Follow
from models.user_models import User

class FollowController:
    @staticmethod
    def follow_user(follower_id, username):
        """Sigue a un usuario"""
        # Obtener usuario a seguir
        user = User.find_by_username(username)
        if not user:
            return {"error": "Usuario no encontrado"}, 404
            
        following_id = str(user['_id'])
        
        # No puede seguirse a sí mismo
        if follower_id == following_id:
            return {"error": "No puedes seguirte a ti mismo"}, 400
            
        # Verificar si ya lo sigue
        if Follow.exists(follower_id, following_id):
            return {"error": "Ya sigues a este usuario"}, 400
            
        # Crear nueva relación de seguimiento
        Follow.create(follower_id, following_id)
        
        return {"message": f"Ahora sigues a {username}"}, 200
    
    @staticmethod
    def unfollow_user(follower_id, username):
        """Deja de seguir a un usuario"""
        # Obtener usuario
        user = User.find_by_username(username)
        if not user:
            return {"error": "Usuario no encontrado"}, 404
            
        following_id = str(user['_id'])
        
        # Eliminar relación de seguimiento
        success = Follow.delete(follower_id, following_id)
        
        if success:
            return {"message": f"Has dejado de seguir a {username}"}, 200
        else:
            return {"error": "No estabas siguiendo a este usuario"}, 400

# app/views/response.py
class Response:
    """Clase para formatear respuestas JSON"""
    
    @staticmethod
    def success(data=None, message=None, status_code=200):
        """Formato de respuesta exitosa"""
        response = {}
        
        if message:
            response["message"] = message
            
        if data is not None:
            response.update(data if isinstance(data, dict) else {"data": data})
            
        return response, status_code
    
    @staticmethod
    def error(message, status_code=400):
        """Formato de respuesta de error"""
        return {"error": message}, status_code