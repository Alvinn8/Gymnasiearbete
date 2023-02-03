from my_server import app
from my_server.database_handler import create_connection, db_fetch_all
from my_server.auth import bcrypt, create_user_jwt, login_required, map_access_required, map_part_required
from my_server.oauth_google import create_authorize_url, verify_google_token
from flask import request, abort
import os
import base64


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


@app.route("/api/register/google")
def register_google():

    state = "register-" + os.urandom(32).hex()
    redirect_url = create_authorize_url(state)

    return {
        "success": True,
        "redirect_url": redirect_url,
        "state": state
    }


@app.route("/api/login/google")
def login_google():

    state = "login-" + os.urandom(32).hex()
    redirect_url = create_authorize_url(state)

    return {
        "success": True,
        "redirect_url": redirect_url,
        "state": state
    }


@app.route("/api/login/google/callback", methods=["POST"])
def login_google_callback():
    data = request.json
    code = data["code"]
    action = data["action"]

    if action == "login":

        error, google_account_id, _ = verify_google_token(code)
        if error is not None:
            return error

        conn = create_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, username FROM User WHERE google_account_id = ?",
            (google_account_id,)
        )
        data = cur.fetchone()
        conn.close()

        if data == None:
            return {
                "success": False,
                "error": "Det finns inget konto kopplat till detta Google-konto"
            }

        user_id, username = data

        jwt = create_user_jwt(user_id, username)

        return {
            "success": True,
            "token": jwt
        }

    elif action == "register":

        error, google_account_id, email = verify_google_token(code)
        if error is not None:
            return error

        username = email

        conn = create_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM User WHERE google_account_id = ?",
            (google_account_id,)
        )
        already_has_account = cur.fetchone()[0] > 0

        if already_has_account:
            conn.close()
            return {
                "success": False,
                "error": "Det finns redan ett konto för detta Google konto. Menade du att logga in?"
            }

        cur.execute(
            "SELECT COUNT(*) FROM User WHERE username = ?",
            (username,)
        )
        username_taken = cur.fetchone()[0] > 0

        if username_taken:
            username = username + "-" + os.urandom(16).hex()

        cur.execute(
            "INSERT INTO User (username, google_account_id) VALUES (?, ?)",
            (username, google_account_id)
        )
        user_id = cur.lastrowid
        conn.commit()
        conn.close()

        jwt = create_user_jwt(user_id, username)

        return {
            "success": True,
            "token": jwt
        }

    else:
        abort(400)


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
@map_access_required
def map_info(jwt, map_id):

    conn = create_connection()
    cur = conn.cursor()

    nameData = cur.execute(
        "SELECT name FROM Map WHERE id = ?",
        (map_id,)
    ).fetchone()

    mapPartsData = cur.execute(
        "SELECT id, name FROM MapPart WHERE map_id = ?",
        (map_id,)
    ).fetchall()

    conn.close()

    mapParts = []
    for mapPartData in mapPartsData:
        mapParts.append({
            "id": mapPartData[0],
            "name": mapPartData[1]
        })

    return {
        "success": True,
        "data": {
            "name": nameData[0],
            "mapParts": mapParts
        }
    }


@app.route("/api/map/<map_id>/part/new", methods=["POST"])
@map_access_required
def new_map_part(jwt, map_id):

    name = request.json["name"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO MapPart (name, map_id) VALUES (?, ?)",
        (name, map_id)
    )
    map_part_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": map_part_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/info")
@map_part_required
def map_part_info(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    walls_data = cur.execute(
        "SELECT id, x, y, width, height FROM Wall WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    background_blob = cur.execute(
        "SELECT background FROM MapPart WHERE id = ?",
        (part_id,)
    ).fetchone()

    background = None
    if background_blob is not None:
        background = background_blob[0]

    conn.close()

    walls = []
    for wall_data in walls_data:
        walls.append({
            "id": wall_data[0],
            "x": wall_data[1],
            "y": wall_data[2],
            "width": wall_data[3],
            "height": wall_data[4]
        })

    return {
        "success": True,
        "walls": walls,
        "background": background
    }


@app.route("/api/map/<map_id>/part/<part_id>/background", methods=["POST"])
@map_part_required
def map_part_background(jwt, map_id, part_id):
    conn = create_connection()
    cur = conn.cursor()

    blob = request.json["file"]

    cur.execute(
        "UPDATE MapPart SET background = ? WHERE id = ?",
        (blob, part_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }


@app.route("/api/map/<map_id>/part/<part_id>/wall/new")
@map_part_required
def new_wall(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Wall (map_part_id, x, y, width, height) VALUES (?, ?, ?, ?, ?)",
        (part_id, 0, 0, 10, 40)
    )
    wall_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": wall_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/wall/edit", methods=["POST"])
@map_part_required
def edit_wall(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    data = request.get_json()
    for change in data["changes"]:
        property_to_change = change["property"]
        if property_to_change not in ("x", "y", "width", "height"):
            abort(400)
        cur.execute(
            "UPDATE Wall SET " + property_to_change +
            " = ? WHERE id = ? AND WHERE map_part_id = ?",
            (change["value"], data["id"], part_id)
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
