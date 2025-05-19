from app.models.user_models import User
from app.models.post_models import Post
from bson.objectid import ObjectId


class TimeLineService:
    def __init__(self):
        pass

    @staticmethod
    def timeline_recommend_users(user_id:str):

        current_user:list = User.find_by_id(user_id)["following"]
            
        all_followings_user = User.collection.find(
            {"_id":{"$in":current_user}},
            {"following":1}
        )

        for i in all_followings_user:
            print(i)
    @staticmethod
    def get_list_user(limit:int=3,projection:dict=None):
        users = User.collection.find().limit(limit)
        if projection is None:
            projection = {
                'username':1,
                'email':1,
                'profile_pic_url':1,
                '_id':1
            }
        users = User.collection.find(
            {},
            projection
        ).limit(limit)

        
        return list(users)