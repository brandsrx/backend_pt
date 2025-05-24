from datetime import datetime
from bson.objectid import ObjectId
from app.database import db


class Notification:
    collection = db['notification']

    @staticmethod
    def create(user_id,username,profile_pic_url,reason):
        
        notification = {
            "user":{
                "user_id":user_id,
                "username":username,
                "profile_pic_url":profile_pic_url,
            },
            "reason":reason,
            "create_at":datetime.utcnow()
        }
        
        result = Notification.collection.insert_one(notification)
        
        return str(result.inserted_id)
    
    @staticmethod
    def find_notifications(user_id):
        return list(Notification.collection.find({'user_id':user_id}))
    
    @staticmethod
    def delete(notifaction_id,user_id):
        result = Notification.collection.delete_one({
            "_id":ObjectId(notifaction_id),
            "user_id":user_id
        })
        
        return result.deleted_count>0
        