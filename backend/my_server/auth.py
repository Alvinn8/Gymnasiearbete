from functools import wraps
from flask import request
import jwt
from my_server import app

# https://blog.loginradius.com/engineering/guest-post/securing-flask-api-with-jwt/

def decode_jwt(f):
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
