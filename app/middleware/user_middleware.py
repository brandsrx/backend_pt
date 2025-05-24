from flask import redirect,request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity,get_jwt
from functools import wraps

def verify_current_user(redirect_to="/profile"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verifica el token si existe, pero no lanza error si no hay uno
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            current_username = claims.get('username')
            username = request.view_args.get("username")
            if current_username == username:
                return redirect(redirect_to)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
