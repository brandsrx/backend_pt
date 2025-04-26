from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.post_service import PostService

post_bp = Blueprint('post', __name__)

@post_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    result, status_code = PostService.create_post(
        user_id=user_id,
        content=data.get('content'),
        media_urls=data.get('media_urls', [])
    )
    
    return jsonify(result), status_code

@post_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    result, status_code = PostService.get_post(post_id)
    
    return jsonify(result), status_code

@post_bp.route('/posts', methods=['GET'])
def get_posts():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    username = request.args.get('username')
    
    result, status_code = PostService.get_posts(username, page, limit)
    
    return jsonify(result), status_code

@post_bp.route('/posts/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()
    
    result, status_code = PostService.delete_post(post_id, user_id)
    
    return jsonify(result), status_code

@post_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_feed():
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    result, status_code = PostService.get_feed(user_id, page, limit)
    
    return jsonify(result), status_code

@post_bp.route('/posts/<post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    result, status_code = PostService.like_post(post_id)
    
    return jsonify(result), status_code
