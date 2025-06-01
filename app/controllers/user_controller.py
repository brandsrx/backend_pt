from flask import Blueprint, request, jsonify, current_app,url_for
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from flask_jwt_extended import jwt_required,get_jwt_identity,verify_jwt_in_request
from datetime import datetime, timedelta
from app.services.user_service import UserService
from bson import ObjectId
from services.time_line_service import TimeLineService
from app.models.post_models import Post
from app.services.post_service import PostService
from app.middleware.user_middleware import verify_current_user
from app.extensions.redis_extencion import redis_client
from app.utils.upload_file import UploadFile
import json


# Create Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route("/profile/picture",methods=["PUT"])
@jwt_required()
def update_picture_profile():
    user_id = get_jwt_identity()
    image = request.form.get('profile_pic_url')
    update_file = UploadFile(username=user_id,target_folder='profile')
    path_url = update_file.process_image(file=image)
    if url is None:
        return jsonify({'error':'No se pudo procesar la imagen'}),400
    url = url_for('static',filename=path_url,_external=True)
    result = UserService.update_photo_profile(user_id,new_url=url)

    if result is False:
       return jsonify({'error':'ocurrio un error a la hora de actualizar la imagen'}),500

    return jsonify({'message':'Imagen actulizada correctamente'}),200 



@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    
    data = request.get_json()
    
    try:
        # Fields that can be updated
        update_data = {}
        for field in ['username', 'email', 'bio']:
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

@user_bp.route("/check-follower", methods=["POST"])
def check_follower():
    data = request.get_json()
    user_id = get_jwt_identity()
    follower_id = data.get("followerId")

    try:
        result = UserService.verify_follower(user_id=user_id,follower_id=follower_id)

        return jsonify({"isFollowing": result is not None}),200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route('/<username>', methods=['GET'])
def get_user_by_username(username):
    """Get public user profile by username"""
    user = UserService.get_user_by_username(username)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_id = str(user['_id'])
    try:
        post = Post.find_by_user(user_id)
        processed_posts = [
                {
                    "id": str(post['_id']),
                    "content": post['content'],
                    "media_urls": post.get('media_urls', []),  # Usa get() para campos opcionales
                    "likes_count": post.get('likes_count', 0),
                    "reposts_count": post.get('reposts_count', 0),
                    "created_at": post['created_at'].isoformat(),  # Convierte datetime a ISO string
                    "author": {
                        "id": user_id,  # Asume que 'user' está disponible en el contexto
                        "username": user['username'],
                        "profile_pic_url": user.get('profile_pic_url', '')
                    }
                }
                for post in Post.collection.find({"user_id": user_id})
            ]
    except Exception:
        processed_posts=[]
    # Remove sensitive information
    user_data = {
            "id":str(user['_id']),
            "username":user['username'],
            "email":user['email'],
            "bio": user['bio'],
            "profile_pic_url":user['profile_pic_url'],
            "followers": len(user['followers']),
            "following": len(user['following']),
            "posts":processed_posts
        } 
    # Include email only if user allows it
    if user.get('privacy', {}).get('show_email', False):
        user_data['email'] = user['email']
    #add en redis
    return jsonify({
        'user': user_data
    }), 200


@user_bp.route('/<username>/follow', methods=['POST'])
@jwt_required()
def follow_user(username):
    """Follow a user"""
    user_id = get_jwt_identity()
    redis_key = f"following:{user_id}"
    target_user = UserService.get_user_by_username(username)
    key_verify = f"recommendations:users:{user_id}"
    if redis_client.exists(key_verify):
        redis_client.delete(key_verify)
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
    target_user_id = str(target_user['_id'])

    if redis_client.exists(redis_key):
        redis_client.sadd(redis_key,target_user_id)
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
    redis_key = f"following:{user_id}"
    key_verify = f"recommendations:users:{user_id}"
    if redis_client.exists(key_verify):
        redis_client.delete(key_verify) 
    if not target_user:
        return jsonify({'message': 'User not found'}), 404
        
    target_user_id = str(target_user['_id'])
    if redis_client.exists(redis_key):
        redis_client.srem(redis_key,target_user_id)
    try:
        if UserService.unfollow_user(user_id, target_user_id):
            return jsonify({'message': f'Unfollowed {username}'}), 200
        else:
            return jsonify({'message': 'Error unfollowing user'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error unfollowing user: {str(e)}")
        return jsonify({'message': 'Error unfollowing user'}), 500


import json

@user_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    skip = int(request.args.get('skip', 0))
    
    if not query:
        return jsonify({'message': 'Missing search query'}), 400
    
    # Key para Redis que identifica la búsqueda con parámetros
    redis_key = f"search:{query}:{limit}:{skip}"
    
    # Intentamos obtener resultados cacheados
    cached = redis_client.get(redis_key)
    if cached:
        # Si existe cache, devolvemos directamente
        return cached, 200, {'Content-Type': 'application/json'}
    
    # Si no hay cache, hacemos las búsquedas en BD
    users = UserService.search_users(query, limit, skip)
    
    users_data = []
    for user in users:
        user_data = {
            'username': user['username'],
            'bio': user['bio'],
            'profile_pic_url': user['profile_pic_url']
        }
        if user.get('privacy', {}).get('show_email', False):
            user_data['email'] = user['email']
        users_data.append(user_data)
    
    
    
    response = {
        'users': users_data,
        'count_users': len(users_data),
    }
    
    # Guardamos en Redis el resultado serializado a JSON con expiración (p.ej. 1 hora)
    redis_client.set(redis_key, json.dumps(response), ex=3600)
    
    return jsonify(response), 200



@user_bp.get("/recommend")
@jwt_required()
def users_recommend():
    user_id = get_jwt_identity()
    users:list = TimeLineService.get_list_user(user_id=user_id)
    if users != []:
        cache_key = f"recommendations:users:{user_id}"
        if redis_client.exists(cache_key) and users != []:
            cached = redis_client.get(cache_key)
            return jsonify(json.loads(cached))
        users = [{
            'username':user['username'],
            'profile_pic_url':user['profile_pic_url']}
            for user in users
            ]
        redis_client.set(cache_key, json.dumps(users), ex=3600)
        return users
    return []