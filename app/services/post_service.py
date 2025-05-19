from app.models.post_models import Post,Comment
from app.models.user_models import User
from app.services.user_service import UserService
from typing import List, Dict


class PostService:
    @staticmethod
    def create_post(user_id, content, media_urls=None):
        """Crea una nueva publicación"""
        if not content:
            return {"error": "El contenido es requerido"}, 400
            
        # Limitar el contenido a 280 caracteres como Twitter
        if len(content) > 280:
            return {"error": "El contenido no puede superar los 280 caracteres"}, 400
            
        post_id = Post.create(user_id, content, media_urls)
        
        return {
            "message": "Publicación creada correctamente",
            "post_id": post_id
        }, 201

    @staticmethod
    def get_post(post_id):
        """Obtiene una publicación por su ID"""
        post = Post.find_by_id(post_id)
        
        if not post:
            return {"error": "Publicación no encontrada"}, 404
            
        # Obtener datos del autor
        user = User.find_by_id(post['user_id'])
        
        post_data = {
            "id": str(post['_id']),
            "content": post['content'],
            "media_urls": post.get('media_urls', []),
            "likes_count": post.get('likes_count', 0),
            "comment_count":post.get('comment_count',0),
            "created_at": post['created_at'].isoformat(),
            "author": {
                "id": str(user['_id']),
                "username": user['username'],
                "profile_pic_url": user.get('profile_pic_url', '')
            }
        }
        
        return post_data, 200
    
    @staticmethod
    def get_posts(username=None, page=1, limit=20):
        """Obtiene publicaciones con paginación"""
        skip = (page - 1) * limit
        
        # Filtrar por usuario (opcional)
        user_id = None
        if username:
            user = User.find_by_username(username)
            if not user:
                return {"error": "Usuario no encontrado"}, 404
            user_id = str(user['_id'])
            
            posts = Post.find_by_user(user_id, skip, limit)
        else:
            # Si no hay username, traer los más recientes de todos
            posts = list(Post.collection.find()
                        .sort("created_at", -1)
                        .skip(skip)
                        .limit(limit))
        
        posts_list = []
        for post in posts:
            # Obtener datos del autor
            post_user = User.find_by_id(post['user_id'])
            
            post_data = {
                "id": str(post['_id']),
                "content": post['content'],
                "media_urls": post.get('media_urls', []),
                "likes_count": post.get('likes_count', 0),
                "comment_count":post.get('comments_count',0),
                "created_at": post['created_at'].isoformat(),
                "author": {
                    "id": str(post_user['_id']),
                    "username": post_user['username'],
                    "profile_pic_url": post_user.get('profile_pic_url', '')
                }
            }
            posts_list.append(post_data)
        
        return {
            "posts": posts_list,
            "page": page,
            "limit": limit
        }, 200
    
    @staticmethod
    def delete_post(post_id, user_id):
        """Elimina una publicación si pertenece al usuario"""
        success = Post.delete_by_id(post_id, user_id)
        
        if success:
            return {"message": "Publicación eliminada correctamente"}, 200
        else:
            return {"error": "Publicación no encontrada o no tienes permiso para eliminarla"}, 404
    
    @staticmethod
    def get_feed(user_id, page=1, limit=20):
        """Obtiene el feed personalizado del usuario"""
        # Obtener IDs de usuarios seguidos
        following_ids = UserService.get_following_ids(user_id)
        
        # Incluir las publicaciones propias
        following_ids.append(user_id)
        
        skip = (page - 1) * limit
        
        # Obtener publicaciones del feed
        posts = Post.find_feed_posts(following_ids, skip, limit)
        
        posts_list = []
        for post in posts:
            # Obtener datos del autor
            post_user = User.find_by_id(post['user_id'])
            
            post_data = {
                "id": str(post['_id']),
                "content": post['content'],
                "media_urls": post.get('media_urls', []),
                "likes_count": post.get('likes_count', 0),
                "comment_count":post.get('comment_count',0),
                "created_at": post['created_at'].isoformat(),
                "author": {
                    "id": str(post_user['_id']),
                    "username": post_user['username'],
                    "profile_pic_url": post_user.get('profile_pic_url', '')
                }
            }
            posts_list.append(post_data)
        
        return {
            "posts": posts_list,
            "page": page,
            "limit": limit
        }, 200
    
    @staticmethod
    def like_post(post_id):
        """Da like a una publicación"""
        post = Post.find_by_id(post_id)
        
        if not post:
            return {"error": "Publicación no encontrada"}, 404
            
        success = Post.add_like(post_id)
        
        if success:
            return {"message": "Like añadido correctamente"}, 201
        else:
            return {"error": "No se pudo añadir el like"}, 500
    @staticmethod
    def dislike_post(post_id):
        """Da like a una publicación"""
        post = Post.find_by_id(post_id)
        
        if not post:
            return {"error": "Publicación no encontrada"}, 404
            
        success = Post.delete_like(post_id)
        
        if success:
            return {"message": "Dislike añadido correctamente"}, 201
        else:
            return {"error": "No se pudo añadir el dislike"}, 500
    @staticmethod
    def comment_post(post_id,username,profile_pic_url,text_comment):
        """Create comment of post samone post_id"""
        post = Post.find_by_id(post_id)
        if not post:
            return {"error":"Publicacion no encontrada"},404
        
        comment = Post.add_comment(post_id,username,profile_pic_url,text_comment)
        if comment:
            return {"message":"Coment created"},201
        return {"Error":"coment not created"},500

    @staticmethod    
    def view_comment(post_id):
        comment = Comment.view_comments(post_id)
        if comment is None or comment == []:
            return {'message':"no data"},204
        return comment,200
    
    @staticmethod
    def delete_comment(post_id,comment_id):
        comment = Comment.delete_comment(post_id,comment_id)
        if comment:
            return {'message':"Comment delete"},200
        return {'error':"comment no delete"},400
        
    @staticmethod
    def search_posts(query: str, page: int = 1, limit: int = 20) -> Dict:
        """Buscar posts por contenido o título y devolverlos con formato de feed"""
        skip = (page - 1) * limit
        pattern = f".*{query}.*"
        regex = {"$regex": pattern, "$options": "i"}

        posts = Post.collection.find(
            {"$or": [{"title": regex}, {"content": regex}]}
        ).skip(skip).limit(limit)
        
        posts_list = []
        for post in posts:
            post_user = User.find_by_id(post['user_id'])
            post_data = {
                "id": str(post['_id']),
                "content": post.get('content', ''),
                "media_urls": post.get('media_urls', []),
                "likes_count": post.get('likes_count', 0),
                "comment_count": post.get('comment_count', 0),
                "created_at": post['created_at'].isoformat() if 'created_at' in post else '',
                "author": {
                    "id": str(post_user['_id']),
                    "username": post_user.get('username', ''),
                    "profile_pic_url": post_user.get('profile_pic_url', '')
                }
            }
            posts_list.append(post_data)

        return {
            "posts": posts_list,
            "page": page,
            "limit": limit
        }, 200