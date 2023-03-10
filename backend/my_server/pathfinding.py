import math
from my_server.database_handler import create_connection

def a_star_find_shortest_path(map_id, start_point_id, end_point_id):
    # https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode

    conn = create_connection()
    cur = conn.cursor()

    all_points = cur.execute(
        """SELECT id, x, y FROM Point WHERE map_part_id IN (
            SELECT id FROM MapPart WHERE map_id = ?
        )
        """,
        (map_id,)
    ).fetchall()

    all_point_connections = cur.execute(
        """SELECT id, point_a_id, point_b_id FROM PointConnection
            WHERE TODO""", # TODO
        (map_id,)
    ).fetchall()

    conn.close()
    
    # A set of points that have been discovered
    open_set = set()

    # A dictionary where the map is a point id and the value is the id of the point
    # that came before the key. This can be used to recreate the shortest path after
    # we find the end.
    previous = {}

    # A dictionary of point id to the smallest distance currently known to get to the point.
    # This is the actual distance from the start to the point.
    # If no value is present, the distance is set to infinity
    g_score = {}

    # We are at the starting point, so the distance is 0
    g_score[start_point_id] = 0

    # A dictionary of point id to the predicted distance for a path if the path
    # were to go trough this point.
    # f(x) = g(x) + h(x)
    # Where g(x) is stored in g_score, and
    # where h(x) is our heuristic function which predicts the distance to get to
    # the end point. This is defined as the bird's-eye-view distance, aka the
    # "perfect" distance to get from A to B using the distance formula.
    # If no value is present, the distance is set to infinity
    f_score = {}
    f_score[start_point_id] = 0

    # While the open set isn't empty
    while len(open_set) > 0:
        # Get the next point in openSet that has the lowest fScore. In other words, get
        # the point which we _think_ will be the shortest path
        current_id = None
        current_f_score = math.inf # Infinity
        for point_id in open_set:
            point_f_score = f_score[point_id]
            # The value defaults to infinity
            if point_f_score is None:
                point_f_score = math.inf
            