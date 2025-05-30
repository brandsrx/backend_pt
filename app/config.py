import os
from datetime import timedelta

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'clave-secreta')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

    #Configuracion para las imagenes
    UPLOAD_FOLDER = 'static/uploads'
    MAX_IMAGE_SIZE = 50*1024*1024
    MAX_IMAGE_FILES = 10
    IMAGE_QUALITY = 80
    MAX_DIMENSION = 1200
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

    #Configuracion para la conexion con MongoDB
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = 'social_network_db'

    #Configuracion para la conexion con Redis
    REDIS_URL = os.environ.get("REDIS_URI","redis://localhost:6379/0")
