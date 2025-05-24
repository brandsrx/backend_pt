import time
from flask import Blueprint, request, jsonify,current_app,url_for
from app.services.user_service import UserService
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from datetime import datetime,timedelta,timezone
from app.extensions.redis_extencion import redis_client
from app.utils.upload_file import UploadFile
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def register():
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        bio = request.form.get('bio', '')
        is_private = request.form.get('is_private', 'false').lower() == 'true'
        image = request.files.get('profile_pic_url')

        if not username or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400
        user_id = UserService.create_user(
            username=username,
            email=email,
            password=password,
            bio=bio,
            profile_pic_url="",
            is_private=is_private
        )

        if image:
            uploader = UploadFile(user_id, 'profile')
            saved_path = uploader.process_image(image)
            url = url_for('static', filename=saved_path, _external=True)
            UserService.update_user_profile(user_id, {'profile_pic_url': url})

        token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=24),
            additional_claims={'username': username}
        )

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user_id
        }), 201

    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Error registering user")
        return jsonify({'message': 'Error registering user'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in a user"""
    data = request.get_json()
    
    try:
        # Get credentials
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'message': 'Missing username/email or password'}), 400
            
        # Authenticate user
        user = UserService.authenticate_user(username_or_email, password)
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
            
        
        token = create_access_token(identity=str(user['_id']),  
                            expires_delta=timedelta(hours=24),  
                            additional_claims={
                                'username': user['username'],  
                                'exp': datetime.now(timezone.utc) + timedelta(hours=24) 
                            })
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({'message': 'Error logging in'}), 500


@auth_bp.post('/logout')
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    exp = get_jwt()['exp']
    ttl = exp-int(time.time())

    redis_client.setex(f"revoked:{jti}",ttl,"true")
    return jsonify(msg="Token revocado exitosamente"),200