import redis
from pymongo import MongoClient
from datetime import timedelta
import json
from functools import wraps

class CacheManager:
    def __init__(self, app=None):
        self.redis_client = None
        self.mongo_client = None
        self.app = None
        
        if app is not None:
            self.init_app(app)
    
    def get_from_cache(self, key):
        """Obtiene datos de Redis"""
        cached_data = self.redis_client.get(key)
        return json.loads(cached_data) if cached_data else None
    
    def set_to_cache(self, key, data, ttl=None):
        """Guarda datos en Redis con tiempo de expiración"""
        if ttl is not None:
            self.redis_client.setex(key, timedelta(seconds=ttl), json.dumps(data))
        else:
            self.redis_client.set(key, json.dumps(data))
    
    def invalidate_cache(self, *keys):
        """Elimina una o varias claves de Redis"""
        for key in keys:
            self.redis_client.delete(key)
    
    def cacheable(self, key_prefix, ttl=3600):
        """
        Decorador para cachear resultados de funciones.
        
        Ejemplo:
        @cache_manager.cacheable(key_prefix='user_posts', ttl=300)
        def get_user_posts(user_id):
            # Lógica para obtener posts
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Genera una clave única basada en los argumentos
                cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args)}:{':'.join(f'{k}={v}' for k, v in kwargs.items())}"
                
                # Intenta obtener de caché
                cached = self.get_from_cache(cache_key)
                if cached is not None:
                    self.app.logger.debug(f'Cache hit for key: {cache_key}')
                    return cached
                
                # Si no está en caché, ejecuta la función y guarda el resultado
                result = f(*args, **kwargs)
                self.set_to_cache(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
    
    def cache_update(self, *key_prefixes):
        """
        Decorador para invalidar caché después de operaciones de escritura.
        
        Ejemplo:
        @cache_manager.cache_update('user_posts')
        def create_post(user_id, post_data):
            # Lógica para crear post
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                result = f(*args, **kwargs)
                
                # Invalida todas las claves relacionadas con los prefijos
                for prefix in key_prefixes:
                    keys = self.redis_client.keys(f"{prefix}:*")
                    if keys:
                        self.redis_client.delete(*keys)
                
                return result
            return wrapper
        return decorator