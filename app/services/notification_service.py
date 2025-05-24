from datetime import datetime
from typing import List,Optional,Any
from app.models.notifiaction_model import Notification

class NotificationService:
    
    @staticmethod
    def get_all_notification(user_id:str)->list:
        return Notification.find_notifications(user_id=user_id)
    
    @staticmethod
    def create_notification(user_id:str,username:str,profile_pic_url:str,reason:str):
        return Notification.create(user_id,username,profile_pic_url,reason)
    
    @staticmethod
    def delete_notification(notification_id,user_id):
        return Notification.delete(notifaction_id=notification_id,user_id=user_id)