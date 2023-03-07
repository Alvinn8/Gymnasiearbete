from flask import request
from my_server import app
from my_server.auth import map_access_required
from my_server.database_handler import create_connection

@app.route("/api/map/<map_id>/room_category/new", methods=["POST"])
@map_access_required
def new_room_category(jwt, map_id):
    name = request.json["name"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO RoomCategory (name, map_id) VALUES (?, ?)",
        (name, map_id)
    )
    room_category_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": room_category_id
    }