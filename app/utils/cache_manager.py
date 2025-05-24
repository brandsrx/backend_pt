import redis
import json
from bson import ObjectId
from pymongo.collection import Collection
from app.models.post_models import Post

class CacheManager:
    def __init__(self, redis_client: redis.Redis, default_post_ttl=3600, default_id_list_ttl=300):
        self.redis = redis_client
        self.posts = Post.collection
        self.post_ttl = default_post_ttl
        self.id_list_ttl = default_id_list_ttl

    def _serialize(self, doc):
        doc['_id'] = str(doc['_id'])
        return doc

    def _deserialize(self, data):
        return json.loads(data)

    def _post_cache_key(self, post_id):
        return f"post:{post_id}"

    def _user_post_ids_key(self, user_id):
        return f"user_post_ids:{user_id}"

    def _user_feed_key(self, user_id: str):
        return f"user_feed:{user_id}"
    
    def invalidate_user_feed(self, user_id: str):
        self.redis.delete(self._user_feed_key(user_id))

    def get_user_feed(self,user_id):
        key = self._user_feed_key(user_id)
        cached = self.redis.get(key)
        if cached:
            return self._deserialize(cached)
        return False

    def create_user_feed(self, user_id: str, posts):
        """Obtiene el feed cacheado o lo genera consultando MongoDB"""
        key = self._user_feed_key(user_id)
        # Cachear el feed
        self.redis.set(key, json.dumps(posts), ex=60)  # TTL corto (60s)
        return posts

    # -----------------------
    # Post individual
    # -----------------------
    def get_post(self, post_id: str):
        key = self._post_cache_key(post_id)
        cached = self.redis.get(key)
        if cached:
            return self._deserialize(cached)

        post = self.posts.find_one({"_id": ObjectId(post_id)})
        if post:
            data = self._serialize(post)
            self.redis.set(key, json.dumps(data), ex=self.post_ttl)
            return data
        return None

    def cache_post(self, post_data: dict):
        post_id = str(post_data['_id'])
        key = self._post_cache_key(post_id)
        self.redis.set(key, json.dumps(self._serialize(post_data)), ex=self.post_ttl)

    def invalidate_post(self, post_id: str):
        self.redis.delete(self._post_cache_key(post_id))

    # -----------------------
    # Lista de IDs de posts
    # -----------------------
    def get_user_post_ids(self, user_id: str, limit=50):
        key = self._user_post_ids_key(user_id)
        cached = self.redis.get(key)
        if cached:
            return self._deserialize(cached)

        cursor = self.posts.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        post_ids = [str(post['_id']) for post in cursor]
        self.redis.set(key, json.dumps(post_ids), ex=self.id_list_ttl)
        return post_ids

    def invalidate_user_post_ids(self, user_id: str):
        self.redis.delete(self._user_post_ids_key(user_id))

    # -----------------------
    # Posts de un usuario
    # -----------------------
    def get_user_posts(self, user_id: str):
        post_ids = self.get_user_post_ids(user_id)
        posts = []
        for pid in post_ids:
            post = self.get_post(pid)
            if post:
                posts.append(post)
        return posts

    # -----------------------
    # Añadir un nuevo post
    # -----------------------
    def add_post(self, user_id: str, post_data: dict):
        result = self.posts.insert_one(post_data)
        post_data['_id'] = result.inserted_id

        self.cache_post(post_data)
        self.invalidate_user_post_ids(user_id)
        self.invalidate_user_feed(user_id)
        
        return str(result.inserted_id)
