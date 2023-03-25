from my_server import app
from my_server.auth import login_required
from my_server.database_handler import create_connection
from flask import request

@app.route("/api/map/<map_id>/favorite_room/list")
@login_required
def list_favorites(jwt, map_id):
    conn = create_connection()
    cur = conn.cursor()

    favorites_data = cur.execute(
        "SELECT room_id FROM FavoriteRoom WHERE user_id = ?",
        (jwt["user"]["id"],)
    ).fetchall()

    favorites = [favorite_data[0] for favorite_data in favorites_data]

    conn.close()

    return {
        "success": True,
        "favorites": favorites
    }

@app.route("/api/map/<map_id>/favorite_room/add", methods=["POST"])
@login_required
def mark_favorite(jwt, map_id):
    room_id = request.json["roomId"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO FavoriteRoom (room_id, user_id) VALUES (?, ?)",
        (room_id, jwt["user"]["id"])
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }

@app.route("/api/map/<map_id>/favorite_room/remove", methods=["POST"])
@login_required
def unmark_favorite(jwt, map_id):
    room_id = request.json["roomId"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM FavoriteRoom WHERE room_id = ? AND user_id = ?",
        (room_id, jwt["user"]["id"])
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }