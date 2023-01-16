from my_server import app
from my_server.database_handler import create_connection
from flask import request
from flask_bcrypt import generate_password_hash

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

@app.post("/api/register")
def register():
    json = request.json
    username = json["username"]
    password = json["password"]

    hashed_password = generate_password_hash(password)

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO User (username, password) VALUES (?, ?)", (username, password))
    conn.close()

    return {
        "username": username
    }, 201