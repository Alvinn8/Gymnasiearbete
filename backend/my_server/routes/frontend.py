from my_server import app, is_production
from flask import request, send_file, send_from_directory, abort

FRONTEND_FOLDER = "../frontend" if is_production else "../../frontend"

# All requests to routes that accept html, for example /, /login, /maps, etc.
# all need to go to the same file because routing is done client side.
@app.route("/", defaults={"text": ""})
@app.route("/<path:text>")
def index_html(text):
    if (request.accept_mimetypes.accept_html):
        return send_file(FRONTEND_FOLDER + "/dist/index.html")
    abort(404)


@app.route("/assets/<asset_name>")
def assets(asset_name):
    return send_from_directory(FRONTEND_FOLDER + "/dist/assets", asset_name)