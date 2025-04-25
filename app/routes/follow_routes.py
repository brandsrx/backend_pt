from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.follow_controller import FollowController

follow_bp = Blueprint('follow', __name__)

@follow_bp.route('/<username>', methods=['POST'])
@jwt_required()
def follow_user(username):
    follower_id = get_jwt_identity()
    
    result, status_code = FollowController.follow_user(follower_id, username)
    
    return jsonify(result), status_code

@follow_bp.route('/unfollow/<username>', methods=['POST'])
@jwt_required()
def unfollow_user(username):
    follower_id = get_jwt_identity()
    
    result, status_code = FollowController.unfollow_user(follower_id, username)
    
    return jsonify(result), status_code