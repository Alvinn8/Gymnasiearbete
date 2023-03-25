from flask import request
from my_server import app
from my_server.auth import map_access_required, map_part_required, map_view_access
from my_server.database_handler import create_connection, db_to_json
import time

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
        "SELECT PointConnection.id, point_a_id, point_b_id FROM PointConnection " +
        "JOIN Point AS point_a ON point_a.id = point_a_id " +
        "JOIN Point AS point_b ON point_b.id = point_b_id " +
        "WHERE point_a.map_part_id = ? OR point_b.map_part_id = ?",
        (part_id, part_id)
    ).fetchall()

    rooms_data = cur.execute(
        "SELECT Room.id, door_at_point_id, name, Room.x, Room.y, Room.width, Room.height, category_id FROM Room " +
        "JOIN Point ON Point.id = door_at_point_id " +
        "WHERE Point.map_part_id = ?",
        (part_id,)
    ).fetchall()

    map_part_data = cur.execute(
        "SELECT name, background, background_scale, z FROM MapPart WHERE id = ?",
        (part_id,)
    ).fetchone()

    staircases_data = cur.execute(
        "SELECT id, x, y, width, height, connects_to, rotation_deg FROM Staircase WHERE map_part_id = ?",
        (part_id,)
    ).fetchall()

    name = map_part_data[0]
    background = map_part_data[1]
    background_scale = map_part_data[2]
    z = map_part_data[3]

    conn.close()

    walls = db_to_json(walls_data, ["id", "x", "y", "width", "height"])
    points = db_to_json(points_data, ["id", "x", "y"])
    point_connections = db_to_json(point_connections_data, ["id", "point_a_id", "point_b_id"])
    rooms = db_to_json(rooms_data, ["id", "doorAtPointId", "name", "x", "y", "width", "height", "categoryId"])
    staircases = db_to_json(staircases_data, ["id", "x", "y", "width", "height", "connectsTo", "rotationDeg"])

    return {
        "success": True,
        "name": name,
        "z": z,
        "walls": walls,
        "points": points,
        "rooms": rooms,
        "point_connections": point_connections,
        "background": background,
        "background_scale": background_scale,
        "staircases": staircases
    }


@app.route("/api/map/<map_id>/part/<part_id>/brief_info")
@map_view_access
def map_part_brief_info(map_id, part_id):

    t0 = time.time()

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
        "SELECT Room.id, door_at_point_id, name, Room.x, Room.y, Room.width, Room.height, category_id FROM Room " +
        "JOIN Point ON Point.id = door_at_point_id " +
        "WHERE Point.map_part_id = ?",
        (part_id,)
    ).fetchall()

    staircases_data = cur.execute(
        """SELECT Staircase.id, Staircase.map_part_id, Staircase.x, Staircase.y, Staircase.width, Staircase.height, Staircase.connects_to, ConnectedMapPart.z, ConnectedMapPart.z - MapPart.z, Staircase.rotation_deg FROM Staircase
            JOIN MapPart ON MapPart.id = Staircase.map_part_id
            LEFT JOIN Staircase AS ConnectedStaircase ON Staircase.connects_to = ConnectedStaircase.id
            LEFT JOIN MapPart AS ConnectedMapPart ON ConnectedStaircase.map_part_id = ConnectedMapPart.id
            WHERE Staircase.map_part_id = ?
        """, (part_id,)
    ).fetchall()

    conn.close()

    walls = db_to_json(walls_data, ["id", "x", "y", "width", "height"])
    points = db_to_json(points_data, ["id", "x", "y"])
    rooms = db_to_json(rooms_data, ["id", "doorAtPointId", "name", "x", "y", "width", "height", "categoryId"])
    staircases = db_to_json(staircases_data, ["id", "mapPartId", "x", "y", "width", "height", "connectsTo", "connectsToZ", "deltaZ", "rotationDeg"])

    t1 = time.time()

    print(f"brief_info took {(t1 - t0):.3f} seconds")

    return {
        "success": True,
        "name": part_data[2],
        "z": part_data[3],
        "walls": walls,
        "points": points,
        "rooms": rooms,
        "offsetX": part_data[0],
        "offsetY": part_data[1],
        "rotationDeg": part_data[4],
        "staircases": staircases
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
