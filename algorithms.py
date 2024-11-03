from collections import deque
import heapq

# Finding the shortest path in a city map using BFS
def BFS(graph, start, destination):
    queue = deque([[start]])  # Queue for BFS paths to explore
    visited = set()  # Set to track visited intersections

    while queue:
        path = queue.popleft()
        current_intersection = path[-1]

        # Check if we have reached the destination
        if current_intersection == destination:
            return None, path  # Return None for distance to match format of DFS and Dijkstra

        if current_intersection not in visited:
            visited.add(current_intersection)

            for neighbor in graph.get(current_intersection, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None, None  # Return None for both if no path found

# Finding the path using DFS
def DFS(graph, start, end, visited=None, path=None, dist=0):
    if visited is None:
        visited = set()
    if path is None:
        path = [start]

    if start == end:
        return dist, path

    visited.add(start)

    for node, weight in graph[start]['adj'].items():  # Adjusted to match Dijkstra’s structure
        if node not in visited:
            new_path = DFS(graph, node, end, visited, path + [node], dist + weight)  # Changed `dfs` to `DFS`
            if new_path:
                return new_path

    return None, None  # Return None if no path is found

# Finding the shortest path using Dijkstra's algorithm
def Dijkstra(graph, source, destination):
    # Step 1: Initialize distances to infinity and set source distance to 0
    distances = {node: float('inf') for node in graph}
    distances[source] = 0

    priority_queue = [(0, source)]  # Priority queue to store distance and node information
    previous_nodes = {node: None for node in graph}  # Dictionary to keep track of the shortest path

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == destination:
            break

        # Skip if the distance is already higher than recorded
        if current_distance > distances[current_node]:
            continue

        # Check all neighbors of the current node
        for neighbor, weight in graph[current_node].get('adj', {}).items():  # Adjusted for consistency
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the shortest path from source to destination
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()  # Reversing the path to start from the source

    return distances[destination], path if distances[destination] != float('inf') else (None, None)  # Handle unreachable nodes
