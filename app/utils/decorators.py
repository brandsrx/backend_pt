from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity,verify_jwt_in_request

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error":str(e)}),401
    return wrapper