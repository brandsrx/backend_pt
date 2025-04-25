from models.user_models import User
from models.post_models import Post
from models.follow_models import Follow
from werkzeug.security import generate_password_hash

class UserController:
    @staticmethod
    def get_current_user(user_id):
        """Obtiene información del usuario actual"""
        user = User.find_by_id(user_id)
        
        if not user:
            return {"error": "Usuario no encontrado"}, 404
            
        user_data = {
            "id": str(user['_id']),
            "username": user['username'],
            "email": user['email'],
            "bio": user.get('bio', ''),
            "profile_pic_url": user.get('profile_pic_url', ''),
            "created_at": user.get('created_at').isoformat()
        }
        
        return user_data, 200
    
    @staticmethod
    def get_user_by_username(username):
        """Obtiene información de un usuario por su username"""
        user = User.find_by_username(username)
        
        if not user:
            return {"error": "Usuario no encontrado"}, 404
            
        user_id = str(user['_id'])
        followers_count = Follow.count_followers(user_id)
        following_count = Follow.count_following(user_id)
        
        user_data = {
            "id": user_id,
            "username": user['username'],
            "bio": user.get('bio', ''),
            "profile_pic_url": user.get('profile_pic_url', ''),
            "followers_count": followers_count,
            "following_count": following_count,
            "created_at": user.get('created_at').isoformat()
        }
        
        return user_data, 200
    
    @staticmethod
    def update_user(user_id, data):
        """Actualiza la información de un usuario"""
        update_data = {}
        
        if 'bio' in data:
            update_data['bio'] = data['bio']
            
        if 'profile_pic_url' in data:
            update_data['profile_pic_url'] = data['profile_pic_url']
            
        if 'email' in data:
            # Verificar que el email no exista en otra cuenta
            existing_user = User.find_by_email(data['email'])
            if existing_user and str(existing_user['_id']) != user_id:
                return {"error": "Email ya está registrado"}, 400
            update_data['email'] = data['email']
            
        if 'password' in data and data['password']:
            update_data['password'] = generate_password_hash(data['password'])
            
        if not update_data:
            return {"error": "No hay datos para actualizar"}, 400
            
        success = User.update(user_id, update_data)
        
        if success:
            return {"message": "Usuario actualizado correctamente"}, 200
        else:
            return {"message": "No se realizaron cambios"}, 200