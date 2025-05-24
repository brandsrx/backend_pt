from app.extensions.redis_extencion import redis_client
from bson.objectid import ObjectId
from pymongo import DESCENDING

import time
from app.models.user_models import User
from app.models.post_models import Post

MAX_FEED_GLOBAL = 500


class FeedCache:

    @staticmethod
    def repopulate_user_feed(user_id):
        user_id = str(user_id)
        followings = User.get_following_by_user_id(user_id)
  
        for following_id in followings:
            redis_client.sadd(f"following:{user_id}", str(following_id))
        redis_client.delete(f"feed:{user_id}")
        
        for following_id in followings:

            posts = list(Post.collection.find(
                {"user_id": str(following_id)},
                {"_id": 1}
            ))
            for post in posts:
                post_id = str(post["_id"]) 
                print(post_id) 
                redis_client.zadd(f"feed:{user_id}", {post_id: time.time()})
    @staticmethod
    def repopulate_global_feed():
        posts = list(Post.collection.find({}).sort("created_at",DESCENDING).limit(100))
        for post in posts:
            FeedCache.add_post_to_feed(
                user_id=post["user_id"],
                post_id=str(post["_id"]),
                created_at=time.time()
            )
    @staticmethod
    def add_post_to_feed(user_id,post_id):
        followers_cache = redis_client.smembers(f"followers:{user_id}")
        if not followers_cache:
            for follower_id in User.get_followers_by_user_id(user_id):
                redis_client.sadd(f"followers:{user_id}",str(follower_id))
                redis_client.zadd(f"feed:{follower_id}",{post_id:time.time()})

        for follower_id in followers_cache:
            redis_client.zadd(f"feed:{follower_id}",{post_id:time.time()})
        
        redis_client.zadd("feed:global",{post_id:time.time()})
        redis_client.zremrangebyrank("feed:global", 0, -MAX_FEED_GLOBAL-1)
    @staticmethod
    def get_feed_global(page=1,limit=20):
        start = (page-1)*limit
        end = start+limit-1
        return redis_client.zrevrange('feed:global',start,end)
    @staticmethod
    def get_feed_user(user_id:str,count=10):    
        post_ids = redis_client.zrevrange(f"feed:{user_id}",0,count-1)
        return post_ids
        
        


