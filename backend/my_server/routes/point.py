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
            "UPDATE Point SET x = ?, y = ? WHERE id = ? AND map_part_id = ?",
            (point["x"], point["y"], point["id"], part_id)
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }


@app.route("/api/map/<map_id>/part/<part_id>/point/delete", methods=["POST"])
@map_part_required
def delete_point(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    point_id = request.json["id"]

    count = cur.execute(
        "SELECT COUNT(*) FROM PointConnection WHERE point_a_id = ? OR point_b_id = ?",
        (point_id, point_id)
    ).fetchone()[0]

    if (count > 0):
        conn.close()
        return {
            "success": False,
            "error": "Ta bort punkanslutningar innan du raderar punkten"
        }

    count = cur.execute(
        "SELECT COUNT(*) FROM Room WHERE door_at_point_id = ?",
        (point_id,)
    ).fetchone()[0]

    if (count > 0):
        conn.close()
        return {
            "success": False,
            "error": "Ta bort rum kopplade till punkten innan du raderar punkten"
        }

    cur.execute(
        "DELETE FROM Point WHERE id = ? AND map_part_id = ?",
        (point_id, part_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
