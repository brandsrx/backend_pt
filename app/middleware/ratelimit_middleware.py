from flask import request, jsonify
from app.extensions.redis_extencion import redis_client
import time

def rate_limiter(limit=100, period=60):
    def decorator(f):
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate_limit:{ip}"
            current = redis_client.get(key)

            if current and int(current) >= limit:
                return jsonify({"error": "Too many requests"}), 429

            # Incrementa el contador
            pipe = redis_client.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, period)  # Expira en 'period' segundos
            pipe.execute()

            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
