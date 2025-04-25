from flask import Blueprint, request, jsonify
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    result, status_code = AuthController.register(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        bio=data.get('bio', ''),
        profile_pic_url=data.get('profile_pic_url', '')
    )
    
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    result, status_code = AuthController.login(
        username=data.get('username'),
        password=data.get('password')
    )
    
    return jsonify(result), status_code