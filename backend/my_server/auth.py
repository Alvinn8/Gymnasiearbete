from functools import wraps
from flask import request
import jwt
from my_server import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# https://blog.loginradius.com/engineering/guest-post/securing-flask-api-with-jwt/

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not "Authorization" in request.headers:
            return {
                "success": False,
                "error": "Unauthorized",
                "message": "No Authorization header"
            }, 401
        
        parts = request.headers["Authorization"].split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return {
                "success": False,
                "error": "Unauthorized",
                "message": "Authorization header must be a Bearer token (JWT)"
            }, 401
        token = parts[1]

        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

        return f(data, *args, **kwargs)
    return decorated

def create_jwt(dictionary):
    return jwt.encode(dictionary, app.config["SECRET_KEY"], "HS256")

def create_user_jwt(user_id, username):
    return create_jwt({
        "user": {
            "id": user_id,
            "name": username
        }
    })