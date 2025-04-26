from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from app.models.user_models import User

class UserService:
    
    @staticmethod
    def create_user(username: str, email: str, password: str, bio: str = '', 
                   profile_pic_url: str = '', is_private: bool = False) -> str:
        return User.create(
            username=username,
            email=email,
            password=password,
            bio=bio,
            profile_pic_url=profile_pic_url,
            is_private=is_private
        )
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        return User.find_by_id(user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        return User.find_by_username(username)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        return User.find_by_email(email)
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> Optional[Dict]:
        # Try to find the user by username or email
        if '@' in username_or_email:
            user = User.find_by_email(username_or_email)
        else:
            user = User.find_by_username(username_or_email)
            
        # Verify password if user exists
        if user and User.check_password(user, password):
            return user
        return None
    
    @staticmethod
    def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
        return User.update_profile(user_id, update_data)
    
    @staticmethod
    def update_privacy_settings(user_id: str, privacy_settings: Dict[str, bool]) -> bool:
        return User.update_privacy(user_id, privacy_settings)
    
    @staticmethod
    def update_notification_settings(user_id: str, notification_settings: Dict[str, bool]) -> bool:
        return User.update_notifications(user_id, notification_settings)
    
    @staticmethod
    def change_user_password(user_id: str, current_password: str, new_password: str) -> bool:
        return User.change_password(user_id, current_password, new_password)
    
    @staticmethod
    def follow_user(user_id: str, target_user_id: str) -> bool:
        if user_id == target_user_id:
            raise ValueError("Un usuario no puede seguirse a sí mismo")
            
        # Check if users exist
        user = User.find_by_id(user_id)
        target_user = User.find_by_id(target_user_id)
        
        if not user or not target_user:
            return False
            
        # Check if already following
        if target_user_id in user.get('following', []):
            return True  # Already following
            
        # Add to following and followers lists
        User.collection.update_one(
            {"_id": user_id},
            {"$addToSet": {"following": target_user_id}}
        )
        
        User.collection.update_one(
            {"_id": target_user_id},
            {"$addToSet": {"followers": user_id}}
        )
        
        return True
    
    @staticmethod
    def unfollow_user(user_id: str, target_user_id: str) -> bool:
       
        # Remove from following and followers lists
        User.collection.update_one(
            {"_id": user_id},
            {"$pull": {"following": target_user_id}}
        )
        
        User.collection.update_one(
            {"_id": target_user_id},
            {"$pull": {"followers": user_id}}
        )
        
        return True
    
    @staticmethod
    def get_followers(user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
       
        user = User.find_by_id(user_id)
        if not user:
            return []
            
        follower_ids = user.get('followers', [])
        return list(User.collection.find(
            {"_id": {"$in": follower_ids}},
            {"password": 0}  # Exclude password field
        ).skip(skip).limit(limit))
        
    @staticmethod
    def get_following_ids(user_id:str)->Optional[Dict]:
        pass
    
    @staticmethod
    def get_following(user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
       
        user = User.find_by_id(user_id)
        if not user:
            return []
            
        following_ids = user.get('following', [])
        return list(User.collection.find(
            {"_id": {"$in": following_ids}},
            {"password": 0}  # Exclude password field
        ).skip(skip).limit(limit))
    
    @staticmethod
    def search_users(query: str, limit: int = 20, skip: int = 0) -> List[Dict]:
      
        # Create regex pattern for case-insensitive search
        pattern = f".*{query}.*"
        regex = {"$regex": pattern, "$options": "i"}
        
        # Search in username and bio fields
        return list(User.collection.find(
            {"$or": [{"username": regex}, {"bio": regex}]},
            {"password": 0}  # Exclude password field
        ).skip(skip).limit(limit))