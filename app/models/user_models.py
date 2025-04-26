from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
import re

class User:
    collection = db['users']
    
    # Validaciones
    @staticmethod
    def validate_email(email):
        """Valida que el email tenga un formato correcto"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_bio(bio):
        """Valida que la bio no exceda 160 caracteres"""
        return isinstance(bio, str) and len(bio) <= 160
    
    @staticmethod
    def create(username, email, password, bio='', profile_pic_url='', is_private=False):
        """Crea un nuevo usuario con configuraciones iniciales"""
        # Validaciones
        if not User.validate_email(email):
            raise ValueError("El email no es válido")
        if not isinstance(password, str) or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        if not User.validate_bio(bio):
            raise ValueError("La bio no puede exceder 160 caracteres")
        
        # Verificar unicidad
        if User.find_by_username(username):
            raise ValueError("El nombre de usuario ya está en uso")
        if User.find_by_email(email):
            raise ValueError("El email ya está en uso")
        
        user = {
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "bio": bio,
            "profile_pic_url": profile_pic_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "privacy": {
                "is_private": is_private,  
                "show_email": False,       
                "allow_mentions": True    
            },
            "notifications": {
                "new_follower": True,      
                "likes": True,            
                "mentions": True,          
                "direct_messages": True    
            },
            "followers": [],           
            "following": []               
        }
        
        result = User.collection.insert_one(user)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(user_id):
        """Busca un usuario por su ID"""
        try:
            return User.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def find_by_username(username):
        """Busca un usuario por su nombre de usuario"""
        return User.collection.find_one({"username": username})
    
    @staticmethod
    def find_by_email(email):
        """Busca un usuario por su email"""
        return User.collection.find_one({"email": email})
    
    @staticmethod
    def update_profile(user_id, update_data):
        """Actualiza datos del perfil (username, email, bio, profile_pic_url)"""
        # Validaciones
        if 'username' in update_data:
            if not User.validate_username(update_data['username']):
                raise ValueError("El nombre de usuario no es válido")
            if User.find_by_username(update_data['username']) and User.find_by_id(user_id)['username'] != update_data['username']:
                raise ValueError("El nombre de usuario ya está en uso")
        
        if 'email' in update_data:
            if not User.validate_email(update_data['email']):
                raise ValueError("El email no es válido")
            if User.find_by_email(update_data['email']) and User.find_by_id(user_id)['email'] != update_data['email']:
                raise ValueError("El email ya está en uso")
        
        if 'bio' in update_data and not User.validate_bio(update_data['bio']):
            raise ValueError("La bio no puede exceder 160 caracteres")
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_privacy(user_id, privacy_settings):
        """Actualiza configuraciones de privacidad"""
        # Validaciones
        valid_keys = {'is_private', 'show_email', 'allow_mentions'}
        if not all(key in valid_keys for key in privacy_settings):
            raise ValueError("Configuraciones de privacidad inválidas")
        
        result = User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "privacy": privacy_settings,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_notifications(user_id, notification_settings):
        """Actualiza preferencias de notificaciones"""
        # Validaciones
        valid_keys = {'new_follower', 'likes', 'mentions', 'direct_messages'}
        if not all(key in valid_keys for key in notification_settings):
            raise ValueError("Configuraciones de notificaciones inválidas")
        
        result = User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "notifications": notification_settings,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Cambia la contraseña del usuario"""
        user = User.find_by_id(user_id)
        if not user or not User.check_password(user, current_password):
            raise ValueError("Contraseña actual incorrecta")
        
        if not isinstance(new_password, str) or len(new_password) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")
        
        result = User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": generate_password_hash(new_password),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def check_password(user, password):
        """Verifica la contraseña de un usuario"""
        return check_password_hash(user['password'], password)
    
    @staticmethod
    def ensure_indexes():
        """Crea índices en la colección para optimizar consultas"""
        User.collection.create_index("username", unique=True)
        User.collection.create_index("email", unique=True)
        User.collection.create_index([("followers", 1)])
        User.collection.create_index([("following", 1)])