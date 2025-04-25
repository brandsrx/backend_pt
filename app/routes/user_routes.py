from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.user_controller import UserController

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    
    result, status_code = UserController.get_current_user(user_id)
    
    return jsonify(result), status_code

@user_bp.route('/<username>', methods=['GET'])
def get_user_by_username(username):
    result, status_code = UserController.get_user_by_username(username)
    
    return jsonify(result), status_code

@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    result, status_code = UserController.update_user(user_id, data)
    
    return jsonify(result), status_code
