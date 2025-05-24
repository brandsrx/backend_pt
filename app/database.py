from pymongo import MongoClient, ASCENDING,DESCENDING
from app.config import Config
from pymongo.errors import OperationFailure
# Cliente MongoDB
client = MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]
def init_db():
    def ensure_index(collection, keys, **kwargs):
        index_name = kwargs.get('name', '_'.join(f"{k}_{v}" for k, v in keys))
        existing_indexes = collection.index_information()
        
        if index_name not in existing_indexes:
            try:
                collection.create_index(keys, **kwargs)
            except OperationFailure as e:
                if e.code not in (85, 86):  # Ignora conflictos de índices existentes
                    raise

    # Aplicar índices
    ensure_index(db.users, [('username', ASCENDING)], unique=True, name='username_unique')
    ensure_index(db.users, [('email', ASCENDING)], unique=True, name='email_unique')

    # Mejor índice para posts con paginación por fecha
    ensure_index(db.posts, [('user_id', ASCENDING), ('created_at', DESCENDING)], name='post_user_date_index')

    # Índice follow único
    ensure_index(db.follows, [('follower_id', ASCENDING), ('following_id', ASCENDING)], unique=True, name='follow_relation_unique')

    # Índice inverso para listar seguidores (opcional)
    ensure_index(db.follows, [('following_id', ASCENDING), ('follower_id', ASCENDING)], name='follow_inverse_index')

    #indices para posts
    ensure_index(db.posts, [('user_id', ASCENDING), ('created_at', DESCENDING)], name='post_user_date_index')

    
    return db