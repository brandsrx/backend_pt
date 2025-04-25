import os
from datetime import timedelta

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'clave-secreta')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = 'social_network_db'
