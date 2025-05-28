from flask import Blueprint, request, jsonify,current_app,url_for
from flask_jwt_extended import jwt_required, get_jwt_identity,verify_jwt_in_request
from app.services.post_service import PostService
from app.extensions.redis_extencion import redis_client
from app.middleware.ratelimit_middleware import rate_limiter
from app.utils.upload_file import UploadFile
from app.utils.feed_cache import FeedCache
from datetime import datetime
import json
import os

post_bp = Blueprint('post', __name__)

def reload_feed_machine():
    post_ids:list = FeedCache.get_feed_global()  
    if post_ids == []:
        FeedCache.repopulate_global_feed()
    return FeedCache.get_feed_global()

@post_bp.route('/', methods=['GET'])
@rate_limiter(limit=100, period=60)
def get_posts():
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    post_ids:list = []

    if user_id is  None:
        post_ids = reload_feed_machine()
    else:    
        post_ids:list = FeedCache.get_feed_user(user_id,10)
        if post_ids == []:
            FeedCache.repopulate_user_feed(user_id)
            post_ids:list = FeedCache.get_feed_user(user_id,10)
            
    if post_ids == []:
        post_ids = reload_feed_machine()
    result, status_code = PostService.get_posts(post_ids, page, limit)
    return jsonify(result), status_code


@post_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    content = request.form.get('content', '')
    files = request.files.getlist('image')  # múltiples archivos con el campo 'image'

    uploader = UploadFile(username=user_id, target_folder="posts")
    saved_paths = uploader.process_images(files)

    urls = [
        url_for('static', filename=path, _external=True)
        for path in saved_paths
    ]


    result, status_code = PostService.create_post(
        user_id=user_id,
        content=content,
        media_urls=urls
    )
    FeedCache.add_post_to_feed(user_id,result['post_id'])

    return jsonify(result),status_code
    

@post_bp.route('/<post_id>', methods=['GET'])
def get_post(post_id):
    result, status_code = PostService.get_post(post_id)
    return jsonify(result), status_code

@post_bp.route("/<post_id>",methods=["PUT"])
def update_post(post_id):
    user_id = get_jwt_identity()
    content = request.form.get('content', '')
    files = request.files.getlist('image')
    urls = None
    if files != []:
        uploader = UploadFile(username=user_id, target_folder="posts")
        saved_paths = uploader.process_images(files)

        urls = [
            url_for('static', filename=path, _external=True)
            for path in saved_paths
        ]
    result,status_code = PostService.update_post(post_id,user_id=user_id,content=content,urls=urls)
    return jsonify(result),status_code


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