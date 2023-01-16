from flask import Flask
from my_server.config import Config
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object(Config)

CORS(app)

from my_server import routes, error