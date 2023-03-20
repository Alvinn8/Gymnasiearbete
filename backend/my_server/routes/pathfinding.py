from flask import request
from my_server import app
from my_server import pathfinding
from my_server.database_handler import create_connection, db_to_json
import math

@app.route("/api/map/pathfinding/find_path", methods=["POST"])
def pathfind():
    data = request.get_json()
    start_point_id = data["startPointId"]
    end_point_id = data["endPointId"]

    path_point_ids = pathfinding.a_star_find_shortest_path(start_point_id, end_point_id)

    return handle_path_point_ids(path_point_ids)

@app.route("/api/map/pathfinding/find_closest", methods=["POST"])
def find_closest():
    data = request.get_json()
    start_point_id = data["startPointId"]
    end_category_id = data["endCategoryId"]

    path_point_ids = pathfinding.dijkstra_find_closest(start_point_id, end_category_id)

    return handle_path_point_ids(path_point_ids)

def handle_path_point_ids(path_point_ids):
    if path_point_ids is None:
        return {
            "success": False
        }
    
    conn = create_connection()
    cur = conn.cursor()
    path_data = cur.execute(
        f"""SELECT Point.id, x + offset_x, y + offset_y, z, rotation_deg FROM Point
            JOIN MapPart ON map_part_id = MapPart.id
            WHERE Point.id IN ({",".join(["?"] * len(path_point_ids))})""",
            # This is still safe from SQL injections as we are only creating the question
            # marks in the SQL query. The data is still safely passed as a prepared statement.
        path_point_ids
    ).fetchall()
    conn.close()

    path = []

    # path_data is ordered incorrectly because SQL will order by the primary key,
    # but we want to order by the pathfinding result.
    for point_id in path_point_ids:
        for point_data in path_data:
            if point_data[0] == point_id:
                rotation_deg = point_data[4]
                x = point_data[1]
                y = point_data[2]

                # If there is rotation we must rotate the point using a rotation matrix
                if rotation_deg != 0:
                    # https://en.wikipedia.org/wiki/Rotation_matrix
                    # Rotate around the following rotation matrix by multiplying the coordinates
                    #
                    # [ cos θ   -sin θ ]
                    # [ sin θ    cos θ ]
                    #
                    rotation_rad = math.radians(rotation_deg)
                    sin = math.sin(rotation_rad)
                    cos = math.cos(rotation_rad)
                    new_x = cos * x - sin * y
                    new_y = sin * x + cos * y
                    x = new_x
                    y = new_y

                path.append({
                    "id": point_id,
                    "x": x,
                    "y": y,
                    "z": point_data[3]
                })

    return {
        "success": True,
        "path": path
    }