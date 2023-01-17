from my_server import app
from my_server.database_handler import create_connection
from flask import request
from flask_bcrypt import generate_password_hash

@app.post("/api/register")
def register():
    json = request.json
    username = json["username"]
    password = json["password"]

    conn = create_connection()
    cur = conn.cursor()

    count = cur.execute(
        "SELECT COUNT(*) FROM User WHERE username = ?",
        (username,)
    ).fetchone()[0]

    if count > 0:
        return {
            "success": False,
            "error": "Användarnamnet är upptaget"
        }

    hashed_password = generate_password_hash(password)

    cur.execute(
        "INSERT INTO User (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )
    conn.commit()
    conn.close()

    return {
        "success": True
    }, 201

@app.route("/api/test")
def test(jwt):
    return jwt