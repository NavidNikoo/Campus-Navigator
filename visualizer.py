import time
from graph import csuf_campus_map, csuf_locations
from matplotlib.widgets import TextBox
from pyproj import Transformer
import matplotlib.pyplot as plt
import osmnx as ox
import contextily as ctx
from shapely.geometry import box
import geopandas as gpd
from shapely.geometry import Point


start_ax = plt.axes([0.075, 0.05, 0.2, 0.04])
end_ax = plt.axes([0.35, 0.05, 0.2, 0.04])

start_textbox = TextBox(start_ax, 'Start:')
end_textbox = TextBox(end_ax, 'End:')

# Store the text elements so we can clear them later
exec_time_text = None
dist_text = None
walking_time_text = None

def plot_exec_time(start_t, end_t):
    global exec_time_text
    if exec_time_text:
        exec_time_text.remove()  # Clear previous text
    exec_time_text = plt.text(1.50, .75, f"Execution time: {end_t - start_t}", color='blue', fontsize=12,
                              transform=plt.gca().transAxes)
    exec_time_text.set_bbox(dict(facecolor='white', alpha=1, edgecolor='blue'))

def plot_dist(dist):
    global dist_text, walking_time_text
    if dist_text:
        dist_text.remove()  # Clear previous text
    if walking_time_text:
        walking_time_text.remove()  # Clear previous text

    avg_walking_speed = 1.42
    walking_time_min = (dist / avg_walking_speed) / 60
    dist_text = plt.text(1.50, 0.50, f"Distance: {dist:.2f} meters", color='blue', fontsize=12, transform=plt.gca().transAxes)
    dist_text.set_bbox(dict(facecolor='white', alpha=1, edgecolor='blue'))
    walking_time_text = plt.text(1.50, 0.25, f"Estimated Walking Time: {walking_time_min:.2f} minutes", color='blue', fontsize=12,
                                 transform=plt.gca().transAxes)
    walking_time_text.set_bbox(dict(facecolor='white', alpha=1, edgecolor='blue'))



def err_invalid():
    start_textbox.set_val("Invalid")
    end_textbox.set_val("Invalid")

def convert_coords(coords_list):
    gdf = gpd.GeoDataFrame(geometry=[Point(x, y) for y, x in coords_list], crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)  # Convert to Web Mercator or whatever projection your map uses
    return [(point.x, point.y) for point in gdf.geometry]


def run_algo(graph, algo, start, end, fig, ax):
    # Step 1: Validate the start and end nodes
    if start not in graph or end not in graph:
        print("Invalid start or end location.")
        return

    # Step 2: Start timing for performance measurement
    s_t = time.perf_counter()

    # Step 3: Run the selected algorithm to find a path
    result = algo(graph, start, end)

    # Step 4: If result is None, exit and print a message
    if result is None:
        print("No path found.")
        return

    # Step 5: Handle result for different algorithms (BFS/DFS return path, Dijkstra returns tuple)
    if isinstance(result, tuple):
        dist, path = result  # For Dijkstra
    else:
        path = result
        dist = len(path)  # Estimate distance for BFS/DFS based on path length

    # Step 6: End timing
    e_t = time.perf_counter()

    # Step 7: Plot the path, execution time, and distance
    if path:
        # Clear any previous paths on `ax`
        for line in ax.get_lines():
            line.remove()

        # Plot the new path on the existing map
        plot_path(graph, path, ax)

        # Plot execution time and distance information
        plot_exec_time(s_t, e_t)
        plot_dist(dist)

        # Reattach hover functionality after updating the plot
        on_hover(fig, ax, csuf_locations)

        # Refresh the figure canvas to display updates
        fig.canvas.draw_idle()
    else:
        print("Path not found between start and end.")


def run_accessible_algo(graph, start, end, fig, ax):
    if start not in graph or end not in graph:
        print("Invalid start or end location.")
        return

    # Run accessible pathfinding
    path = dijkstra_accessible(graph, start, end)
    if path:
        plot_path(graph, path, ax)  # Plot accessible path on the map
    else:
        print("No accessible path found between start and end.")

    fig.canvas.draw_idle()  # Refresh the plot


def clear_textboxes(event):
    start_textbox.set_val('')
    end_textbox.set_val('')


def plot_campus():
    # Convert the graph nodes to a GeoDataFrame in Web Mercator
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(csuf_campus_map)
    gdf_nodes = gdf_nodes.to_crs(epsg=3857)

    # Filter only campus locations based on `csuf_locations`
    campus_locations = {coords: name for name, coords in csuf_locations.items()}
    location_nodes = gdf_nodes[gdf_nodes.apply(lambda row: (row['y'], row['x']) in campus_locations, axis=1)]

    # Calculate bounds directly from csuf_locations
    longitudes = [coords[1] for coords in campus_locations.keys()]
    latitudes = [coords[0] for coords in campus_locations.keys()]
    west_bound, east_bound = min(longitudes) - 0.0005, max(longitudes) + 0.0005
    south_bound, north_bound = min(latitudes) - 0.0002, max(latitudes) + 0.0009

    # Convert these bounds to Web Mercator projection
    bbox = gpd.GeoDataFrame(geometry=[box(west_bound, south_bound, east_bound, north_bound)], crs="EPSG:4326")
    bbox = bbox.to_crs(epsg=3857)
    west, south, east, north = bbox.total_bounds

    # Initialize the plot with explicit bounds and fixed figure size
    fig, ax = plt.subplots(figsize=(10, 10), dpi=75)  # Adjust `figsize` and `dpi` for fixed size at startup

    # Plot only the campus nodes without any edges
    location_nodes.plot(ax=ax, markersize=50, color='red', zorder=2)  # Larger markers for visibility

    # Add OpenStreetMap tiles as the background
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    # Set x and y limits based on calculated campus area bounds
    ax.set_xlim([west, east])
    ax.set_ylim([south, north])

    # Add minimal padding to avoid overlap with GUI
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Optionally, use tight_layout to ensure minimal padding without overlap
    plt.tight_layout(pad=5)

    # Remove axis labels for a cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("California State University, Fullerton")

    # Return fig and ax for further customization (hover, GUI)
    return fig, ax, campus_locations

def on_hover(fig, ax):
    # Create an annotation for displaying the node name
    annot = ax.annotate(
        "", xy=(0,0), xytext=(15,15),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->")
    )
    annot.set_visible(False)

    # Dictionary to store coordinates and location names for easy lookup
    location_coords = {coords: name for name, coords in csuf_locations.items()}

    # Update the annotation position and text
    def update_annot(x, y, name):
        annot.xy = (x, y)
        annot.set_text(name)
        annot.set_visible(True)

    # Event handler for mouse movement
    def hover(event):
        visible = annot.get_visible()
        if event.inaxes == ax:
            for (lat, long), name in location_coords.items():
                # Check if mouse is near a specific location marker
                if abs(event.xdata - long) < 0.0001 and abs(event.ydata - lat) < 0.0001:
                    update_annot(long, lat, name)
                    fig.canvas.draw_idle()
                    return
            if visible:
                annot.set_visible(False)
                fig.canvas.draw_idle()

    # Connect the hover event to the figure
    fig.canvas.mpl_connect("motion_notify_event", hover)

def plot_path(graph, path, ax=None):
    # Ensure we have an existing axis with a background map
    if ax is None:
        fig, ax, _ = plot_campus()
    else:
        # Clear only previous path lines and start/end annotations on the existing axis
        for line in ax.get_lines():
            line.remove()
        for text in ax.texts:
            text.remove()  # Clear previous start/end annotations

    if not path or len(path) < 2:
        print("Path is too short or invalid.")
        return

    # Collect coordinates and convert them to the correct projection if needed
    coords_list = [(graph[node]['coords'][0], graph[node]['coords'][1]) for node in path if 'coords' in graph[node]]
    if len(coords_list) < 2:
        print("Insufficient valid coordinates for plotting.")
        return

    # Convert coordinates to the projection used by the map if necessary
    coords_list = convert_coords(coords_list)
    coords_x, coords_y = zip(*coords_list)

    # Plot path as a line and start/end markers
    ax.plot(coords_x, coords_y, color='cyan', linestyle='-', marker='o', markersize=5, lw=2, zorder=10)

    # Mark start and end points
    start_x, start_y = coords_x[0], coords_y[0]
    end_x, end_y = coords_x[-1], coords_y[-1]
    ax.plot(start_x, start_y, 'go', markersize=10, zorder=11, label='Start')
    ax.plot(end_x, end_y, 'bo', markersize=10, zorder=11, label='End')

    # Annotate start and end points
    ax.annotate('Start', (start_x, start_y), textcoords="offset points", xytext=(-10, -10), ha='center', color='black',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=1), zorder=11)
    ax.annotate('End', (end_x, end_y), textcoords="offset points", xytext=(-10, -10), ha='center', color='black',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=1), zorder=11)

    # Ensure the plot is updated with the path
    ax.figure.canvas.draw_idle()

def plot_location_names(event):
    plt.figure()
    plt.title('')

    text = []
    for location in csuf_locations.keys():
        text.append(f"{location}\n")

    plt.text(0.3, 0.1, ''.join(text), fontsize=10, color='black', transform=plt.gca().transAxes)
    plt.axis('off')
    plt.show()

def on_hover(fig, ax, csuf_locations):
    # Set up coordinate transformation from lat/long to the map's projection
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)  # from lat/long to Web Mercator

    # Initialize an annotation for displaying node names
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->")
    )
    annot.set_visible(False)

    # Convert and store node positions in projected coordinates
    node_positions = {}
    for name, (lat, long) in csuf_locations.items():
        # Transform latitude and longitude to match plot coordinates
        proj_x, proj_y = transformer.transform(long, lat)
        node_positions[name] = (proj_x, proj_y)

    # Function to update the annotation
    def update_annotation(name, x, y):
        annot.xy = (x, y)
        annot.set_text(name)
        annot.set_visible(True)
        fig.canvas.draw_idle()

    # Event handler for hover
    def on_move(event):
        if event.inaxes != ax:
            return  # Ignore events outside the plot area

        for name, (node_x, node_y) in node_positions.items():
            # Check if the cursor is close to a node within a small tolerance
            if abs(node_x - event.xdata) < 20 and abs(node_y - event.ydata) < 20:  # Adjust tolerance as needed
                update_annotation(name, node_x, node_y)
                return

        # Hide the annotation if no node is nearby
        annot.set_visible(False)
        fig.canvas.draw_idle()

    # Connect the hover function to the figure
    fig.canvas.mpl_connect("motion_notify_event", on_move)

