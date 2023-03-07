from flask import request
from my_server import app
from my_server.auth import map_access_required, map_part_required, map_view_access
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/new", methods=["POST"])
@map_access_required
def new_map_part(jwt, map_id):

    json = request.get_json()
    name = json["name"]
    z = json["z"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO MapPart (name, z, map_id) VALUES (?, ?, ?)",
        (name, z, map_id)
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

    rooms_data = cur.execute(
        "SELECT Room.id, door_at_point_id, name, Room.x, Room.y, Room.width, Room.height FROM Room " +
        "JOIN Point ON Point.id = door_at_point_id " +
        "WHERE Point.map_part_id = ?",
        (part_id,)
    ).fetchall()

    map_part_data = cur.execute(
        "SELECT name, background, background_scale, z FROM MapPart WHERE id = ?",
        (part_id,)
    ).fetchone()

    name = map_part_data[0]
    background = map_part_data[1]
    background_scale = map_part_data[2]
    z = map_part_data[3]

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

    rooms = []
    for room_data in rooms_data:
        rooms.append({
            "id": room_data[0],
            "doorAtPointId": room_data[1],
            "name": room_data[2],
            "x": room_data[3],
            "y": room_data[4],
            "width": room_data[5],
            "height": room_data[6]
        })

    return {
        "success": True,
        "name": name,
        "z": z,
        "walls": walls,
        "points": points,
        "rooms": rooms,
        "point_connections": point_connections,
        "background": background,
        "background_scale": background_scale
    }


@app.route("/api/map/<map_id>/part/<part_id>/brief_info")
@map_view_access
def map_part_brief_info(map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    part_data = cur.execute(
        "SELECT offset_x, offset_y, name, z, rotation_deg FROM MapPart WHERE id = ?",
        (part_id,)
    ).fetchone()

    walls_data = cur.execute(
        "SELECT id, x, y, width, height FROM Wall WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    points_data = cur.execute(
        "SELECT id, x, y FROM Point WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    rooms_data = cur.execute(
        "SELECT Room.id, door_at_point_id, name, Room.x, Room.y, Room.width, Room.height FROM Room " +
        "JOIN Point ON Point.id = door_at_point_id " +
        "WHERE Point.map_part_id = ?",
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

    rooms = []
    for room_data in rooms_data:
        rooms.append({
            "id": room_data[0],
            "doorAtPointId": room_data[1],
            "name": room_data[2],
            "x": room_data[3],
            "y": room_data[4],
            "width": room_data[5],
            "height": room_data[6]
        })

    return {
        "success": True,
        "name": part_data[2],
        "z": part_data[3],
        "walls": walls,
        "points": points,
        "rooms": rooms,
        "offsetX": part_data[0],
        "offsetY": part_data[1],
        "rotationDeg": part_data[4]
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


@app.route("/api/map/<map_id>/part/<part_id>/update_offset", methods=["POST"])
@map_part_required
def map_part_update_offset(jwt, map_id, part_id):
    conn = create_connection()
    cur = conn.cursor()

    json = request.get_json()
    offset_x = json["offsetX"]
    offset_y = json["offsetY"]
    rotation_deg = json["rotationDeg"]

    cur.execute(
        "UPDATE MapPart SET offset_x = ?, offset_y = ?, rotation_deg = ? WHERE id = ?",
        (offset_x, offset_y, rotation_deg, part_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
