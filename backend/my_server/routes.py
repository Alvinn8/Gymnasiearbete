from my_server import app
from my_server.database_handler import create_connection, db_fetch, db_fetch_all, db_fetch_one
from my_server.auth import bcrypt, create_user_jwt, login_required
from my_server.oauth_google import create_authorize_url
from flask import request
import os

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
        conn.close()
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
        "SELECT id, password FROM User WHERE username = ?",
        (username,)
    )
    data = cur.fetchone()
    conn.close()

    if data == None:
        return {
            "success": False,
            "error": "Felaktigt användarnamn eller lösenord"
        }

    user_id, correct_password = data
    
    if not bcrypt.check_password_hash(correct_password, password):
        return {
            "success": False,
            "error": "Felaktigt användarnamn eller lösenord"
        }
    
    # The username and password is correct, let's generate a JWT
    jwt = create_user_jwt(user_id, username)

    return {
        "success": True,
        "token": jwt
    }

@app.route("/api/login/google")
def login_google():

    state = os.urandom(32).hex()

    redirect_url = create_authorize_url(state)

    return {
        "success": True,
        "redirect_url": redirect_url,
        "state": state
    }

@app.route("/api/account/info")
@login_required
def account_info(jwt):
    return {
        "success": True,
        "username": jwt["user"]["name"]
    }

@app.route("/api/map/list")
@login_required
def maps(jwt):

    user_id = jwt["user"]["id"]

    data = db_fetch_all(
        """
        SELECT id, name FROM Map
            WHERE id IN (
                SELECT map_id FROM UserMapAccess WHERE user_id = ?
            )
        """,
        (user_id,)
    )

    maps = []
    for map in data:
        maps.append({
            "id": map[0],
            "name": map[1]
        })

    return {
        "success": True,
        "maps": maps
    }

@app.route("/api/map/new", methods=["POST"])
@login_required
def new_map(jwt):
    map_name = request.json["name"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Map (name) VALUES (?)",
        (map_name,)
    )
    map_id = cur.lastrowid

    cur.execute(
        "INSERT INTO UserMapAccess (map_id, user_id) VALUES (?, ?)",
        (map_id, jwt["user"]["id"])
    )

    conn.commit()
    conn.close()

    return {
        "id": map_id
    }

@app.route("/api/map/<map_id>", methods=["DELETE"])
@login_required
def delete_map(jwt, map_id):

    conn = create_connection()
    cur = conn.cursor()

    count = cur.execute(
        "SELECT COUNT(*) FROM UserMapAccess WHERE map_id = ? AND user_id = ?",
        (map_id, jwt["user"]["id"])
    ).fetchone()[0]

    if not count > 0:
        conn.close()
        return {
            "success": False,
            "error": "Insufficent access to the specified map."
        }, 403
    
    # We must delete all related rows too

    cur.execute(
        "DELETE FROM UserMapAccess WHERE map_id = ?",
        (map_id,)
    )

    # Delete the map

    cur.execute(
        "DELETE FROM Map WHERE id = ?",
        (map_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }

@app.route("/api/map/<map_id>/info")
@login_required
def map_info(jwt, map_id):

    conn = create_connection()
    cur = conn.cursor()

    data = cur.execute(
        "SELECT name FROM Map WHERE id = ?",
        (map_id,)
    ).fetchone()

    accessCount = cur.execute(
        "SELECT COUNT(*) FROM UserMapAccess WHERE user_id = ? AND map_id = ?",
        [jwt["user"]["id"], map_id]
    ).fetchone()[0]

    conn.close()

    if data is None or not accessCount > 0:
        return {
            "success": False,
            "error": "Kunde inte hitta kartan"
        }

    return {
        "success": True,
        "name": data[0]
    }