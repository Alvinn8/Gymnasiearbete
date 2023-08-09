from flask import Flask
from my_server.config import Config
from flask_cors import CORS
import os

is_production = False
if os.path.exists("production.txt"):
    is_production = True

if os.environ.get("ENV") == "production":
    is_production = True

if is_production:
    print("Running in production mode.")

app = Flask(__name__)

app.config.from_object(Config)

if not is_production:
    # Only allow CORS in development as the frontend and backend will run on
    # different ports. On production the frontend is served trough flask, therefore
    # the same port so no CORS is necessary.
    CORS(app)

from my_server import error
from my_server.routes import frontend, auth, map, map_part, wall, point, point_connection, room, room_category, pathfinding, staircase, favorite_room, account
