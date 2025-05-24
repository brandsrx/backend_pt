from flask_jwt_extended import JWTManager
from redis import Redis
from flask import Flask
from app.config import Config

jwt = JWTManager()
redis_client = Redis.from_url(Config.REDIS_URL, decode_responses=True)

def init_extensions(app: Flask):
    jwt.init_app(app)
    # Registrar función para verificar tokens revocados
    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return redis_client.get(f"revoked:{jti}") == "true"
