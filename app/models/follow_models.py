from datetime import datetime
from database import db

class Follow:
    collection = db['follows']
    
    @staticmethod
    def create(follower_id, following_id):
        """Crea una nueva relación de seguimiento"""
        follow = {
            "follower_id": follower_id,
            "following_id": following_id,
            "created_at": datetime.utcnow()
        }
        
        result = Follow.collection.insert_one(follow)
        return str(result.inserted_id)
    
    @staticmethod
    def delete(follower_id, following_id):
        """Elimina una relación de seguimiento"""
        result = Follow.collection.delete_one({
            "follower_id": follower_id,
            "following_id": following_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    def exists(follower_id, following_id):
        """Verifica si existe una relación de seguimiento"""
        return Follow.collection.find_one({
            "follower_id": follower_id, 
            "following_id": following_id
        }) is not None
    
    @staticmethod
    def get_following_ids(user_id):
        """Obtiene los IDs de usuarios que un usuario sigue"""
        follows = Follow.collection.find({"follower_id": user_id})
        return [follow['following_id'] for follow in follows]
    
    @staticmethod
    def count_followers(user_id):
        """Cuenta los seguidores de un usuario"""
        return Follow.collection.count_documents({"following_id": user_id})
    
    @staticmethod
    def count_following(user_id):
        """Cuenta a cuántos usuarios sigue el usuario"""
        return Follow.collection.count_documents({"follower_id": user_id})
