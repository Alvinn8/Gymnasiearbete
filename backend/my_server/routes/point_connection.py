from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/point_connection/new", methods=["POST"])
@map_part_required
def new_point_connection(jwt, map_id, part_id):

    data = request.get_json()

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO PointConnection (point_a_id, point_b_id, weight) VALUES (?, ?, ?)",
        (data["point_a_id"], data["point_b_id"], data["weight"])
    )
    point_connection_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": point_connection_id
    }
