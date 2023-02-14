from flask import request
from my_server import app
from my_server.auth import map_access_required, map_part_required, map_view_access
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

    points_data = cur.execute(
        "SELECT id, x, y FROM Point WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    point_connections_data = cur.execute(
        "SELECT PointConnection.id, point_a_id, point_b_id, weight FROM PointConnection " +
        "JOIN Point AS point_a ON point_a.id = point_a_id " +
        "JOIN Point AS point_b ON point_b.id = point_b_id " +
        "WHERE point_a.map_part_id = ? OR point_b.map_part_id = ?",
        (part_id, part_id)
    ).fetchall()

    background_data = cur.execute(
        "SELECT background, background_scale FROM MapPart WHERE id = ?",
        (part_id,)
    ).fetchone()

    background = None
    background_scale = None
    if background_data is not None:
        background = background_data[0]
        background_scale = background_data[1]

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

    points = []
    for point_data in points_data:
        points.append({
            "id": point_data[0],
            "x": point_data[1],
            "y": point_data[2]
        })

    point_connections = []
    for point_connection in point_connections_data:
        point_connections.append({
            "id": point_connection[0],
            "point_a_id": point_connection[1],
            "point_b_id": point_connection[2],
            "weight": point_connection[3]
        })

    return {
        "success": True,
        "walls": walls,
        "points": points,
        "point_connections": point_connections,
        "background": background,
        "background_scale": background_scale
    }

@app.route("/api/map/<map_id>/part/<part_id>/brief_info")
@map_view_access
def map_part_brief_info(map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    walls_data = cur.execute(
        "SELECT id, x, y, width, height FROM Wall WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    points_data = cur.execute(
        "SELECT id, x, y FROM Point WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

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

    points = []
    for point_data in points_data:
        points.append({
            "id": point_data[0],
            "x": point_data[1],
            "y": point_data[2]
        })

    return {
        "success": True,
        "walls": walls,
        "points": points
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


@app.route("/api/map/<map_id>/part/<part_id>/background_scale", methods=["POST"])
@map_part_required
def map_part_background_scale(jwt, map_id, part_id):
    conn = create_connection()
    cur = conn.cursor()

    scale = request.json["scale"]

    cur.execute(
        "UPDATE MapPart SET background_scale = ? WHERE id = ?",
        (scale, part_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
