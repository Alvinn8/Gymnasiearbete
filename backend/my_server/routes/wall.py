from flask import request, abort
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/wall/new", methods=["POST"])
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
    for wall in data["changes"]:
        cur.execute(
            "UPDATE Wall SET x = ?, y = ?, width = ?, height = ? WHERE id = ?",
            (wall["x"], wall["y"], wall["width"], wall["height"], wall["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
