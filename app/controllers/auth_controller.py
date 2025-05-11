from flask import Blueprint, request, jsonify,current_app
from app.services.user_service import UserService
from flask_jwt_extended import create_access_token
from datetime import datetime,timedelta,timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    try:
        # Required fields
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        # Optional fields
        bio = data.get('bio', '')
        profile_pic_url = data.get('profile_pic_url', '')
        is_private = data.get('is_private', False)
        
        # Create user
        user_id = UserService.create_user(
            username=username,
            email=email,
            password=password,
            bio=bio,
            profile_pic_url=profile_pic_url,
            is_private=is_private
        )
        
        token = create_access_token(identity=str(user_id),  
                             expires_delta=timedelta(hours=24),  
                             additional_claims={
                                 'username': username,  
                                 'exp': datetime.now(timezone.utc) + timedelta(hours=24) 
                             })
        
        return jsonify({
            'message': 'User registered successfully',
            'token':token,
            'user_id': user_id
        }), 201
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
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
