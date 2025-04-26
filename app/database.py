from pymongo import MongoClient
from app.config import Config
 
# Cliente MongoDB
client = MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]
 
def init_db():
    # Crear colecciones e índices
    users = db['users']
    posts = db['posts']
    follows = db['follows']
    
    # Índices para mejorar el rendimiento
    users.create_index('username', unique=True)
    users.create_index('email', unique=True)
    posts.create_index('user_id')
    follows.create_index([('follower_id', 1), ('following_id', 1)], unique=True)
    
    return db