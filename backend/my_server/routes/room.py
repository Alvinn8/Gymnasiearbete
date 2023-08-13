from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/room/new", methods=["POST"])
@map_part_required
def new_room(jwt, map_id, part_id):
    json = request.get_json()
    door_at_point_id = json["doorAtPointId"]
    name = json["name"]

    conn = create_connection()
    cur = conn.cursor()

    count = cur.execute(
        "SELECT COUNT(*) FROM Point WHERE Point.id = ? AND map_part_id = ?",
        (door_at_point_id, part_id)
    ).fetchone()[0]

    if not count > 0:
        conn.close()
        return {
            "success": False
        }

    cur.execute(
        "INSERT INTO Room (door_at_point_id, name, x, y, width, height) VALUES (?, ?, ?, ?, ?, ?)",
        (door_at_point_id, name, 10, 10, 40, 40)
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
        category_id = None
        if "categoryId" in room:
            category_id = room["categoryId"]

        cur.execute(
            "UPDATE Room SET name = ?, x = ?, y = ?, width = ?, height = ?, category_id = ? WHERE id = ?",
            (room["name"], room["x"], room["y"],
             room["width"], room["height"], category_id,
             room["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }


@app.route("/api/map/<map_id>/part/<part_id>/room/delete", methods=["POST"])
@map_part_required
def delete_room(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    room_id = request.json["id"]

    count = cur.execute(
        "SELECT COUNT(*) FROM Room JOIN Point ON Room.door_at_point_id = Point.id WHERE Room.id = ? AND map_part_id = ?",
        (room_id, part_id)
    ).fetchone()[0]

    if not count > 0:
        conn.close()
        return {
            "success": False
        }

    cur.execute(
        "DELETE FROM Room WHERE id = ?",
        (room_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
