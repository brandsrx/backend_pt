from datetime import datetime
from bson.objectid import ObjectId
from app.database import db
from concurrent.futures import ThreadPoolExecutor

class Comment:
    colletion = db['comments']
    @staticmethod
    def create(post_id,username,profile_pic_url,text_comment=''):
        
        comment_structerd = {
            "post_id":post_id,
            "user":{
                "username":username,
                "profile_pic_url":profile_pic_url
            },
            "text_comment":text_comment,
            "created_at": datetime.utcnow()
        }
        result = Comment.colletion.insert_one(comment_structerd)
        return True
    @staticmethod
    def view_comments(post_id):
        comments = Comment.colletion.find({'post_id':post_id})
        if comments is None:
            return "no data",404
        data_forma = [
            {
                "id":str(data['_id']),
                "user":data['user'],
                "text_comment":data['text_comment'],
                "created_at":data['created_at']
            }
            for data in comments
        ]
        return data_forma
    
    @staticmethod
    def delete_comment(post_id,comment_id):
        result = Comment.colletion.delete_one({
                "_id":ObjectId(comment_id),
                "post_id":post_id
            }
        )
        return result.deleted_count > 0

class Post:
    collection = db['posts']
    @staticmethod
    def create(user_id, content, media_urls=None):
        """Crea una nueva publicación"""
        if media_urls is None:
            media_urls = []
            
        post = {
            "user_id": user_id,
            "content": content,
            "media_urls": media_urls,
            "comments_count":0,
            "likes_count": 0,
            "created_at": datetime.utcnow()
        }
        
        result = Post.collection.insert_one(post)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(post_id):
        """Busca una publicación por su ID"""
        try:
            return Post.collection.find_one({"_id": ObjectId(post_id)})
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id, skip=0, limit=20):
        """Busca publicaciones de un usuario con paginación"""
        return Post.collection.find({"user_id": user_id})
        
    
    @staticmethod
    def find_feed_posts(user_ids, skip=0, limit=20):
        """Busca publicaciones para el feed basadas en los IDs de usuarios"""
        return list(Post.collection.find({"user_id": {"$in": user_ids}})
                   .sort("created_at", -1)
                   .skip(skip)
                   .limit(limit))
    
    @staticmethod
    def delete_by_id(post_id, user_id):
        """Elimina una publicación por su ID si pertenece al usuario"""
        result = Post.collection.delete_one({
            "_id": ObjectId(post_id),
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    def add_like(post_id):
        """Incrementa el contador de likes de una publicación"""
        result = Post.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"likes_count": 1}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_like(post_id):
        """Decrementar el contador de likes de una publicación"""
        result = Post.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"likes_count": -1}}
        )
        return result.modified_count > 0
    
    
    @staticmethod
    def add_comment(post_id,username,profile_pic_url,text_comment):
        """Add comment of post"""
        Post.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"comments_count": 1}}
        )
        try:
            Comment.create(post_id,username,profile_pic_url,text_comment)
            return True
        except Exception as e:
            return False
        
        
    