from flask import request, abort
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


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
