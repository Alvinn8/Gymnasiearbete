from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/room/new", methods=["POST"])
@map_part_required
def new_room(jwt, map_id, part_id):
    # We may want to verify the point actually is on this map part

    json = request.get_json()
    has_door_at_point_id = json["doorAtPointId"]
    name = json["name"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Room (door_at_point_id, name, x, y, width, height) VALUES (?, ?, ?, ?, ?, ?)",
        (has_door_at_point_id, name, 10, 10, 40, 40)
    )
    room_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": room_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/room/edit", methods=["POST"])
@map_part_required
def edit_room(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    data = request.get_json()
    for room in data["changes"]:
        cur.execute(
            "UPDATE Room SET name = ?, x = ?, y = ?, width = ?, height = ? WHERE id = ?",
            (room["name"], room["x"], room["y"],
             room["width"], room["height"], room["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
