from my_server import app, is_production
from flask import request, send_file, send_from_directory, abort
import os.path

FRONTEND_FOLDER = "../frontend" if is_production else "../../frontend"
INDEX_HTML = FRONTEND_FOLDER + "/dist/index.html"

HAS_PRODUCTION_FILES = os.path.exists(INDEX_HTML)

# All requests to routes that accept html, for example /, /login, /maps, etc.
# all need to go to the same file because routing is done client side.
@app.route("/", defaults={"text": ""})
@app.route("/<path:text>")
def index_html(text):
    if not is_production or not HAS_PRODUCTION_FILES:
        return """
        You need to start the frontend separately and open the frontend.
        You have currently opened the backend (the API) in the browser.
        The frontend is usually hosted on: <a href="http://localhost:4173">http://localhost:4173</a>
        """
    if (request.accept_mimetypes.accept_html):
        return send_file(INDEX_HTML)
    abort(404)


@app.route("/assets/<asset_name>")
def assets(asset_name):
    return send_from_directory(FRONTEND_FOLDER + "/dist/assets", asset_name)