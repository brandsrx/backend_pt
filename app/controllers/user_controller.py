from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime, timedelta
from app.services.user_service import UserService
from bson import ObjectId

# Create Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    # Remove sensitive information
    user_id = get_jwt_identity()
    user_data = UserService.get_user_by_id(user_id=user_id)
    
    if user_data is None:
        return jsonify({"message":"User not exits"}),404
   
    user_data = {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in user_data.items()}
    
    # Eliminar la información sensible (como la contraseña)
    user_data = {k: v for k, v in user_data.items() if k != 'password'}
    return jsonify({
        'user': user_data
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    
    data = request.get_json()
    
    try:
        # Fields that can be updated
        update_data = {}
        for field in ['username', 'email', 'bio', 'profile_pic_url']:
            if field in data:
                update_data[field] = data[field]
                
        if not update_data:
            return jsonify({'message': 'No valid fields to update'}), 400
                
        # Update profile
        if UserService.update_user_profile(user_id, update_data):
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'message': 'Error updating profile'}), 400
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'message': 'Error updating profile'}), 500


@user_bp.route('/privacy', methods=['PUT'])
@jwt_required()
def update_privacy():
    """Update privacy settings"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    try:
        # Get privacy settings
        privacy_settings = {}
        for field in ['is_private', 'show_email', 'allow_mentions']:
            if field in data:
                privacy_settings[field] = bool(data[field])
                
        if not privacy_settings:
            return jsonify({'message': 'No valid privacy settings to update'}), 400
                
        # Update privacy
        if UserService.update_privacy_settings(user_id, privacy_settings):
            return jsonify({'message': 'Privacy settings updated successfully'}), 200
        else:
            return jsonify({'message': 'Error updating privacy settings'}), 400
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating privacy: {str(e)}")
        return jsonify({'message': 'Error updating privacy settings'}), 500


@user_bp.route('/notifications', methods=['PUT'])
@jwt_required()
def update_notifications(current_user):
    """Update notification settings"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    try:
        # Get notification settings
        notification_settings = {}
        for field in ['new_follower', 'likes', 'mentions', 'direct_messages']:
            if field in data:
                notification_settings[field] = bool(data[field])
                
        if not notification_settings:
            return jsonify({'message': 'No valid notification settings to update'}), 400
                
        # Update notifications
        if UserService.update_notification_settings(user_id, notification_settings):
            return jsonify({'message': 'Notification settings updated successfully'}), 200
        else:
            return jsonify({'message': 'Error updating notification settings'}), 400
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating notifications: {str(e)}")
        return jsonify({'message': 'Error updating notification settings'}), 500


@user_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    try:
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'message': 'Missing current or new password'}), 400
                
        # Change password
        if UserService.change_user_password(user_id, current_password, new_password):
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'message': 'Error changing password'}), 400
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error changing password: {str(e)}")
        return jsonify({'message': 'Error changing password'}), 500


@user_bp.route('/<username>', methods=['GET'])
def get_user_by_username(username):
    """Get public user profile by username"""
    user = UserService.get_user_by_username(username)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    # Remove sensitive information
    user_data = {
        'username': user['username'],
        'bio': user['bio'],
        'profile_pic_url': user['profile_pic_url'],
        'created_at': user['created_at']
    }
    
    # Include email only if user allows it
    if user.get('privacy', {}).get('show_email', False):
        user_data['email'] = user['email']
        
    return jsonify({
        'user': user_data
    }), 200


@user_bp.route('/<username>/follow', methods=['POST'])
@jwt_required()
def follow_user(username):
    """Follow a user"""
    user_id = get_jwt_identity()
    target_user = UserService.get_user_by_username(username)
    
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
        
    target_user_id = str(target_user['_id'])
    
    try:
        if UserService.follow_user(user_id, target_user_id):
            return jsonify({'message': f'Now following {username}'}), 200
        else:
            return jsonify({'message': 'Error following user'}), 400
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error following user: {str(e)}")
        return jsonify({'message': 'Error following user'}), 500


@user_bp.route('/<username>/unfollow', methods=['POST'])
@jwt_required()
def unfollow_user(username):
    """Unfollow a user"""
    user_id = get_jwt_identity()
    target_user = UserService.get_user_by_username(username)
    
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
        
    target_user_id = str(target_user['_id'])
    
    try:
        if UserService.unfollow_user(user_id, target_user_id):
            return jsonify({'message': f'Unfollowed {username}'}), 200
        else:
            return jsonify({'message': 'Error unfollowing user'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error unfollowing user: {str(e)}")
        return jsonify({'message': 'Error unfollowing user'}), 500


@user_bp.route('/search', methods=['GET'])
def search_users():
    """Search for users"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    skip = int(request.args.get('skip', 0))
    
    if not query:
        return jsonify({'message': 'Missing search query'}), 400
        
    users = UserService.search_users(query, limit, skip)
    
    # Remove sensitive information
    users_data = []
    for user in users:
        user_data = {
            'username': user['username'],
            'bio': user['bio'],
            'profile_pic_url': user['profile_pic_url']
        }
        
        # Include email only if user allows it
        if user.get('privacy', {}).get('show_email', False):
            user_data['email'] = user['email']
            
        users_data.append(user_data)
    
    return jsonify({
        'users': users_data,
        'count': len(users_data)
    }), 200