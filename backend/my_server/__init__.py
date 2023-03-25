from flask import Flask
from my_server.config import Config
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object(Config)

CORS(app)

from my_server import error
from my_server.routes import frontend, auth, map, map_part, wall, point, point_connection, room, room_category, pathfinding, staircase, favorite_room
