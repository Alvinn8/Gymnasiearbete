from flask import request, abort
from my_server import app
from my_server.database_handler import create_connection
from my_server.auth import bcrypt, create_user_jwt, login_required
from my_server.oauth_google import create_authorize_url, verify_google_token
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
    redirect_url = create_authorize_url(state, request.host)

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
