from flask import request
from my_server import app
from my_server.auth import map_access_required, map_part_required
from my_server.database_handler import create_connection


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
