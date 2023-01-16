from my_server import app
from flask import make_response

@app.route("/api/ping")
def ping():
    return {
        "success": True
    }

@app.route("/api/test")
def test():
    return {
        "data": [
            {
                "title": "Test",
                "content": "Lorem ipsum"
            },
            {
                "title": "Foo",
                "content": "Yo no sé que quiero escribir."
            }
        ]
    }