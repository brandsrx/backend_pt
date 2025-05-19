from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.post_service import PostService
from app.extensions.redis_extencion import redis_client
from app.middleware.ratelimit_middleware import rate_limiter
import json

post_bp = Blueprint('post', __name__)

@post_bp.route('/', methods=['GET'])
@rate_limiter(limit=100, period=60)
def get_posts():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    username = request.args.get('username')
    cache_key = "posts:all"

    cached = redis_client.get(cache_key)
    if cached:
        print("datos en la cache")
        return json.loads(cached)


    result, status_code = PostService.get_posts(username, page, limit)
    redis_client.set(cache_key,json.dumps(result),ex=3600)
    return jsonify(result), status_code


@post_bp.route('/', methods=['POST'])
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

@post_bp.route('/<post_id>', methods=['GET'])
def get_post(post_id):
    result, status_code = PostService.get_post(post_id)
    
    return jsonify(result), status_code


@post_bp.route('/<post_id>', methods=['DELETE'])
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

@post_bp.route('/<post_id>/like', methods=['POST'])
@rate_limiter(limit=100, period=60)
@jwt_required()
def like_post(post_id):
    result, status_code = PostService.like_post(post_id)
    
    return jsonify(result), status_code

@post_bp.route('/<post_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_post_controller(post_id):
    result, status_code = PostService.dislike_post(post_id)
    return jsonify(result), status_code

@post_bp.route('/<post_id>/comment', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    data = request.get_json()
    username = data.get("username")
    profile = data.get("profile_pic_url")
    text_comment = data.get("text_comment")
    
    result, status_code = PostService.comment_post(post_id,username,profile_pic_url=profile,text_comment=text_comment)
    return jsonify(result), status_code

@post_bp.route('/<post_id>/comment', methods=['GET'])
def view_comment_post(post_id):
    result,status_code = PostService.view_comment(post_id)
    return jsonify(result), status_code

@post_bp.delete("/<post_id>/comment/<comment_id>")
@jwt_required()
def delete_comment(post_id,comment_id):
    result,status_code = PostService.delete_comment(post_id,comment_id)
    return jsonify(result),status_code