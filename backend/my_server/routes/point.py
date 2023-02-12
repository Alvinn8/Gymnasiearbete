from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection

@app.route("/api/map/<map_id>/part/<part_id>/point/new", methods=["POST"])
@map_part_required
def new_point(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Point (map_part_id, x, y) VALUES (?, ?, ?)",
        (part_id, 0, 0)
    )
    point_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": point_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/point/edit", methods=["POST"])
@map_part_required
def edit_point(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    data = request.get_json()
    for point in data["changes"]:
        cur.execute(
            "UPDATE Point SET x = ?, y = ? WHERE id = ?",
            (point["x"], point["y"], point["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
