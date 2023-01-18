from my_server import app
from my_server.database_handler import create_connection
from my_server.auth import bcrypt, decode_jwt, create_jwt, login_required
from flask import request

@app.route("/api/register", methods=["POST"])
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

    hashed_password = bcrypt.generate_password_hash(password)

    cur.execute(
        "INSERT INTO User (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )
    conn.commit()
    conn.close()

    return {
        "success": True
    }, 201

@app.route("/api/login", methods=["POST"])
def login():
    json = request.json
    username = json["username"]
    password = json["password"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT (password) FROM User WHERE username = ?",
        (username,)
    )
    data = cur.fetchone()
    conn.close()

    if data == None:
        return {
            "success": False,
            "error": "Felaktigt användarnamn eller lösenord"
        }

    correct_password = data[0]
    
    if not bcrypt.check_password_hash(correct_password, password):
        return {
            "success": False,
            "error": "Felaktigt användarnamn eller lösenord"
        }
    
    # The username and password is correct, let's generate a JWT
    jwt = create_jwt({
        "username": username
    })

    return {
        "success": True,
        "token": jwt
    }

@app.route("/api/account/info")
@decode_jwt
def account_info(jwt):
    return {
        "success": True,
        "username": jwt["username"]
    }

@app.route("/api/test")
@login_required
def test():
    return {
        "success": True
    }