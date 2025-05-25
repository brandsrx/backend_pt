from app.models.user_models import User
from app.models.post_models import Post
from bson.objectid import ObjectId
from app.extensions.redis_extencion import redis_client

class TimeLineService:
    @staticmethod
    def get_list_user(user_id, limit=5, projection=None):
        redis_key = f"following:{user_id}"
        if not redis_client.exists(redis_key):
            followings = User.get_following_by_user_id(user_id)
            
            for following_id in followings:
                redis_client.sadd(f"following:{user_id}", str(following_id))
            # También añadir el propio usuario para excluirse
        redis_client.sadd(redis_key, user_id)
        # Obtener todos los IDs que debo excluir
        excluded_ids = redis_client.smembers(redis_key)
        excluded_object_ids = [ObjectId(uid) for uid in excluded_ids]

        # Proyección por defecto si no se pasa
        if projection is None:
            projection = {
                '_id': 1,
                'username': 1,
                'profile_pic_url': 1,
            }

        # Consulta MongoDB: todos los usuarios que no están en el set de Redis
        users = User.collection.find(
            {"_id": {"$nin": excluded_object_ids}},
            projection
        ).limit(limit)
        return list(users)

