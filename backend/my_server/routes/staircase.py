from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/staircase/new", methods=["POST"])
@map_part_required
def new_staircase(jwt, map_id, part_id):

    z = request.json["z"]
    delta_z = request.json["deltaZ"]

    conn = create_connection()
    cur = conn.cursor()

    # Create a staircase pair

    cur.execute(
        "INSERT INTO Staircase (x, y, width, height, z) VALUES (?, ?, ?, ?)",
        (10, 10, 40, 40, z)
    )
    staircase_a_id = cur.lastrowid

    cur.execute(
        "INSERT INTO Staircase (x, y, width, height, z, connects_to) VALUES (?, ?, ?, ?)",
        (10, 10, 40, 40, z + delta_z, staircase_a_id)
    )
    staircase_b_id = cur.lastrowid

    cur.execute(
        "UPDATE Staircase SET connects_to = ? WHERE id = ?",
        (staircase_b_id, staircase_a_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "idA": staircase_a_id,
        "idB": staircase_b_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/staircase/edit", methods=["POST"])
@map_part_required
def edit_staircase(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    data = request.get_json()
    for staircase in data["changes"]:
        category_id = None

        cur.execute(
            "UPDATE Room SET x = ?, y = ?, width = ?, height = ?, connects_to = ? WHERE id = ?",
            (staircase["x"], staircase["y"],
             staircase["width"], staircase["height"],
             staircase["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
