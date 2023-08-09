from flask import request
from my_server import app
from my_server.auth import login_required, generate_password_hash
from my_server.database_handler import create_connection


@app.route("/api/account/details")
@login_required
def account_details(jwt):
    user_id = jwt["user"]["id"]

    conn = create_connection()
    cur = conn.cursor()

    data = cur.execute(
        "SELECT username, password FROM User WHERE id = ?",
        (user_id,)
    ).fetchone()

    username = data[0]
    password_exists = data[1] != None

    return {
        "success": True,
        "username": username,
        "has_password": password_exists
    }


@app.route("/api/account/change_username", methods=["POST"])
@login_required
def change_username(jwt):
    user_id = jwt["user"]["id"]

    username = request.json["username"]

    conn = create_connection()
    cur = conn.cursor()

    count = cur.execute(
        "SELECT COUNT(*) FROM User WHERE username = ?",
        (username,)
    ).fetchone()[0]

    if count > 0:
        conn.close()
        return {
            "success": False,
            "error": "Användarnamnet är upptaget"
        }

    cur.execute(
        "UPDATE USER SET username = ? WHERE id = ?",
        (username, user_id)
    )
    conn.commit()

    return {
        "success": True
    }


@app.route("/api/account/change_password", methods=["POST"])
@login_required
def change_password(jwt):
    user_id = jwt["user"]["id"]

    password = request.json["password"]
    hashed_password = generate_password_hash(password)

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE USER SET password = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    conn.commit()

    return {
        "success": True
    }
