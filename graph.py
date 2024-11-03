from collections import defaultdict
import osmnx as ox

latitude = 33.88534
longitude = -117.88742


csuf_campus_map = ox.graph_from_point((latitude, longitude), dist=800, network_type='all')


csuf_locations = { # dictionary to hold the location names, and the coordinates associated with them
    "Humanities Building":                       (33.880501635139034, -117.88410082595438),
    "McCarthy Hall":                             (33.879528, -117.885849),
    "Dan Black Hall":                            (33.879118, -117.885543),
    "Pollak Library":                            (33.881666, -117.885414),
    "Titan Student Union":                       (33.881782, -117.888574),
    "College Park Building":                     (33.87757498322724, -117.8834483491749),
    "Langsdorf Hall":                            (33.879007227971314, -117.88434605269099),
    "Mihaylo Hall":                              (33.878878, -117.883526),
    "Gordon Hall":                               (33.87974056822556, -117.88416485364138),
    "Student Recreation Center":                 (33.882864, -117.887791),
    "Parking Structure":                         (33.8820, -117.8844), # which parking structure is this?
    "Titan Gymnasium":                           (33.882957, -117.885811),
    "Engineering South East":                    (33.881937, -117.88299),
    "Engineering North East":                    (33.882659, -117.882995),
    "Computer Science":                          (33.882485, -117.882673),
    "Engineering Building":                      (33.882374, -117.883269),
    "Student Health and Counseling Center":      (33.883322, -117.884282),
    "Ruby Gerontology Center":                   (33.883363, -117.883258),
    "CSUF Biology Greenhouse Complex":           (33.879604, -117.886981),
    "Mackey Auditorium":                         (33.884048, -117.883279),
    "Bookstore/Titan Shops":                     (33.882107, -117.886831),
    "Parking Lot 1":                             (33.881488, -117.882802),
    "Parking Lot C":                             (33.878508, -117.887442),
    "Parking Lot D":                             (33.884262, -117.887828),
    "Parking Lot F":                             (33.88025, -117.882738),
    "Marriott":                                  (33.878579, -117.881847),
    "Visual Arts Center":                        (33.88007014225456, -117.88866610469454),
    "Clayes Performing Arts Center":             (33.880214, -117.88668),
    "Nutwood Parking Structure":                 (33.87915, -117.888547),
    "Athletics Fields":                          (33.883885019638015, -117.8856008766424),
    "Education Classroom Building":              (33.881271257706345, -117.88434071135715),
    "Eastside Parking Structure":                (33.88023716960995, -117.8817502188979),
    "State College Parking Structure":           (33.883144, -117.888601)
}


def create_graph(csuf_campus_map) -> dict:

    graph = defaultdict(dict) #initialize empty graph

    # Copy adjacency
    for source_id, source_data in csuf_campus_map.adj.items():
        for nei_id, nei_data in source_data.items():

            nei_data = nei_data[0]

            #edge data
            if 'name' in nei_data:
                graph[nei_id]['name'] = nei_data['name']
            if 'adj' not in graph[source_id]:
                graph[source_id]['adj'] = {}
            if 'adj' not in graph[nei_id]:
                graph[nei_id]['adj'] = {}
            graph[source_id]['adj'][nei_id] = nei_data['length']

    #Custom Coordinates
    for name, data in csuf_campus_map.nodes(data=True):
        long, lat = data['x'], data['y']
        graph[name]['coords'] = (lat, long)

    return graph

def add_locations(graph) -> None:
    # The OSMNX library only stores street names, not our locations
    # Add our locations to the graph by connecting each location to its nearest street(s)
    for location_name, (lat, long) in csuf_locations.items():
        graph[location_name]['name'] = location_name
        graph[location_name]['adj'] = {}
        graph[location_name]['coords'] = (lat, long)

    for location_name, (lat, long) in csuf_locations.items():
        # Bounds padding
        # Create a square around the building to connect more possible streets
        # Arbitrary value (for now)
    # TESTING REQUIRED
        bp = 0.0001 # unit: long/lat
        top_left = (-bp, -bp)
        top_right = (bp, -bp)
        bottom_left = (-bp, bp)
        bottom_right = (bp, bp)
        for dx, dy in [top_left, top_right, bottom_left, bottom_right]:

            nearest_node_id, dist = ox.distance.nearest_nodes(csuf_campus_map, long + dx, lat + dy, return_dist=True)

            scale = 1
            while nearest_node_id == location_name:
                scale *= 1.4
                nearest_node_id, dist = ox.distance.nearest_nodes(csuf_campus_map, long + dx * scale, lat + dy * scale, return_dist=True)

            graph[location_name]['adj'][nearest_node_id] = dist
            graph[nearest_node_id]['adj'][location_name] = dist

def add_csuf_locations():
    # Add locations as nodes to the graph
    for location, coords in csuf_locations.items():
        csuf_campus_map.add_node(location, x = coords[1], y = coords[0], weight = 1)

