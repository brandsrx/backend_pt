from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User:
    collection = db['users']
    
    @staticmethod
    def create(username, email, password, bio='', profile_pic_url=''):
        """Crea un nuevo usuario"""
        user = {
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "bio": bio,
            "profile_pic_url": profile_pic_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
    def update(user_id, update_data):
        """Actualiza un usuario"""
        update_data['updated_at'] = datetime.utcnow()
        
        result = User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def check_password(user, password):
        """Verifica la contraseña de un usuario"""
        return check_password_hash(user['password'], password)