from functools import wraps
from flask import request
import jwt
from my_server import app
from flask_bcrypt import Bcrypt
from my_server.database_handler import create_connection

bcrypt = Bcrypt(app)

# https://blog.loginradius.com/engineering/guest-post/securing-flask-api-with-jwt/

# A decorator used on routes that require authentication to be used
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

def has_access_to_map(map_id, jwt, cur):
    accessCount = cur.execute(
        "SELECT COUNT(*) FROM UserMapAccess WHERE user_id = ? AND map_id = ?",
        [jwt["user"]["id"], map_id]
    ).fetchone()[0]

    return accessCount > 0

# A decorator used to denote that a route requires login and that the logged in
# user needs to have access to the map wit the id of the map_id parameter
def map_access_required(f):
    @wraps(f)
    @login_required
    def decorated(jwt, map_id, *args, **kwargs):
        
        conn = create_connection()
        cur = conn.cursor()

        if not has_access_to_map(map_id, jwt, cur):
            conn.close()
            return {
                "success": False,
                "error": "Kunde inte hitta kartan"
            }
    
        conn.close()

        return f(jwt, map_id, *args, **kwargs)
    return decorated

# A decorator used to denote that a route requires login and access to a map
# and a map part
def map_part_required(f):
    @wraps(f)
    @login_required
    def decorated(jwt, map_id, part_id, *args, **kwargs):
        
        conn = create_connection()
        cur = conn.cursor()

        if not has_access_to_map(map_id, jwt, cur):
            conn.close()
            return {
                "success": False,
                "error": "Kunde inte hitta kartdelen"
            }
        
        partCount = cur.execute(
            "SELECT COUNT(*) FROM MapPart WHERE id = ? AND map_id = ?",
            (part_id, map_id,)
        ).fetchone()[0]

        if not partCount > 0:
            conn.close()
            return {
                "success": False,
                "error": "Kunde inte hitta kartdelen"
            }
    
        conn.close()

        return f(jwt, map_id, part_id, *args, **kwargs)
    return decorated

# A decorator that denotes that a route requires view access to a map. The map
# must either me public or the user must be logged in to an account with access
# to the map.
def map_view_access(f):
    @wraps(f)
    def decorated(map_id, *args, **kwargs):
        
        conn = create_connection()
        cur = conn.cursor()

        public = cur.execute(
            "SELECT public FROM Map WHERE id = ?",
            (map_id,)
        ).fetchone()

        if public is None:
            return {
                "success": False,
                "error": "Kunde inte hitta kartan"
            }
        
        if public[0] == 0:
            # Private map, we need to verify that the user
            # is logged in and has access to the map.
            # TODO we don't have the jwt here
            conn.close()
            return {
                "success": False,
                "error": "Du har inte tillgång till kartan. Pröva att logga in. Men det kommer inte funka för sidan fungerar inte än... :)"
            }, 403

        conn.close()

        return f(map_id, *args, **kwargs)
    return decorated