from collections import deque
import heapq

# ----------------------
# Breadth-First Search (BFS)
# ----------------------
def BFS(graph, start, destination):
    """
    Find the shortest path in an unweighted graph using Breadth-First Search (BFS).

    Args:
        graph (dict): The graph where each node has an 'adj' key listing adjacent nodes.
        start: The starting node.
        destination: The target node.

    Returns:
        list: The shortest path from start to destination, or None if no path is found.
    """
    # Ensure start and destination nodes exist in the graph
    if start not in graph or destination not in graph:
        print(f"Error: Start '{start}' or destination '{destination}' not in graph.")
        return None

    # Initialize BFS queue with the start node, tracking the path
    queue = deque([[start]])
    visited = set()  # Track visited nodes

    print(f"Starting BFS from '{start}' to '{destination}'")

    while queue:
        # Get the first path from the queue
        path = queue.popleft()
        current_node = path[-1]
        print(f"Visiting node: {current_node}, Path so far: {path}")

        # If the current node is the destination, return the path
        if current_node == destination:
            print(f"BFS found path: {path}")
            return path

        # Explore neighbors if not visited
        if current_node not in visited:
            visited.add(current_node)
            neighbors = graph[current_node].get('adj', [])  # Access adjacent nodes

            if not neighbors:
                print(f"No neighbors found for node {current_node}")

            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = list(path)  # Create a new path including the neighbor
                    new_path.append(neighbor)
                    queue.append(new_path)
                    print(f"Added new path to queue: {new_path}")

    print("BFS could not find a path.")
    return None


# ----------------------
# Depth-First Search (DFS)
# ----------------------
def DFS(graph, start, end, visited=None, path=None, dist=0):
    """
    Find a path between two nodes in a graph using Depth-First Search (DFS).

    Args:
        graph (dict): The graph with nodes having 'adj' keys for neighbors.
        start: The starting node.
        end: The target node.
        visited (set): Nodes already visited to prevent cycles.
        path (list): Accumulated path from start to the current node.
        dist (float): Distance accumulated along the path.

    Returns:
        tuple: A tuple of total distance and path from start to end, or None if no path is found.
    """
    # Check if both start and end nodes are in the graph
    if start not in graph or end not in graph:
        print(f"Error: Start '{start}' or end '{end}' not in graph.")
        return None

    # Initialize visited and path if they are not passed
    if visited is None:
        visited = set()
    if path is None:
        path = [start]

    # If the destination is reached, return the path and distance
    if start == end:
        print(f"DFS found path: {path}")
        return dist, path

    # Mark the current node as visited
    visited.add(start)

    # Recursive DFS on each adjacent node
    for node in graph[start].get('adj', {}):
        if node not in visited:
            new_path = DFS(graph, node, end, visited, path + [node], dist + graph[start]['adj'][node])
            if new_path:
                return new_path

    print("DFS could not find a path.")
    return None


# ----------------------
# Dijkstra's Algorithm
# ----------------------
def Dijkstra(graph, source, destination):
    """
    Find the shortest path in a weighted graph using Dijkstra's algorithm.

    Args:
        graph (dict): The graph where each node has 'adj' for adjacent nodes and weights.
        source: The starting node.
        destination: The target node.

    Returns:
        tuple: Total distance and the path from source to destination, or (None, None) if unreachable.
    """
    # Step 1: Initialize all distances to infinity except the source
    distances = {node: float('inf') for node in graph}
    distances[source] = 0

    # Priority queue for selecting the minimum distance node
    priority_queue = [(0, source)]
    previous_nodes = {node: None for node in graph}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Stop if the destination is reached
        if current_node == destination:
            break

        # Skip if a shorter path has already been found
        if current_distance > distances[current_node]:
            continue

        # Process each neighbor of the current node
        for neighbor, weight in graph[current_node].get('adj', {}).items():
            distance = current_distance + weight

            # Update shortest distance if a new path is found
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the shortest path from destination to source
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()

    return (distances[destination], path) if distances[destination] != float('inf') else (None, None)
