from flask import request
from my_server import app
from my_server.auth import map_access_required
from my_server.database_handler import create_connection, db_to_json


@app.route("/api/map/<map_id>/point_connection/new", methods=["POST"])
@map_access_required
def new_point_connection(jwt, map_id):

    data = request.get_json()

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO PointConnection (point_a_id, point_b_id) VALUES (?, ?)",
        (data["point_a_id"], data["point_b_id"])
    )
    point_connection_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": point_connection_id
    }

@app.route("/api/map/<map_id>/point_connection/remove_all_from_point", methods=["POST"])
@map_access_required
def remove_all_connections_from_point(jwt, map_id):
    point_id = request.json["pointId"]

    conn = create_connection()
    cur = conn.cursor()

    ids_data = cur.execute(
        "SELECT id FROM PointConnection WHERE point_a_id = ? OR point_b_id = ?",
        (point_id, point_id)
    ).fetchall()
    cur.execute(
        "DELETE    FROM PointConnection WHERE point_a_id = ? OR point_b_id = ?",
        (point_id, point_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "ids": db_to_json(ids_data, ["id"])
    }