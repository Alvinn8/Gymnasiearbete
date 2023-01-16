from flask import render_template
from my_server import app
import json

@app.errorhandler(404)
def not_found(error):
    return {
        "error": 404
    }, 404
