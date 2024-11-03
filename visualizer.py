import matplotlib.pyplot as plt # For Visualizations
from matplotlib.widgets import Button, TextBox
import osmnx as ox
import contextily as ctx
from graph import csuf_campus_map, csuf_locations
from matplotlib.widgets import Button, TextBox
import time
from pyproj import Transformer
import matplotlib.pyplot as plt
import osmnx as ox
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point, box


start_ax = plt.axes([0.075, 0.05, 0.2, 0.04])
end_ax = plt.axes([0.35, 0.05, 0.2, 0.04])


start_textbox = TextBox(start_ax, 'Start:')
end_textbox = TextBox(end_ax, 'End:')

def plot_exec_time(start_t, end_t):
    et = plt.text(0.01, 0.01, f"Execution time: {end_t - start_t}", color='red', fontsize=12,
                  transform=plt.gca().transAxes)
    et.set_bbox(dict(facecolor='white', alpha=1, edgecolor='red'))


def plot_dist(dist):
    # in meters, source: google
    avg_walking_speed = 1.42
    walking_time_min = (dist / avg_walking_speed) / 60
    dt = plt.text(0.01, 0.06, f"Distance: {dist:.2f} meters", color='red', fontsize=12, transform=plt.gca().transAxes)
    dt.set_bbox(dict(facecolor='white', alpha=1, edgecolor='red'))
    tt = plt.text(0.01, 0.11, f"Estimated Walking Time: {walking_time_min:.2f} minutes", color='red', fontsize=12,
                  transform=plt.gca().transAxes)
    tt.set_bbox(dict(facecolor='white', alpha=1, edgecolor='red'))


def err_invalid():
    start_textbox.set_val("Invalid")
    end_textbox.set_val("Invalid")


import time
from tkinter import messagebox  # For displaying error messages


def run_algo(graph, algo, start, end):
    # Check if start and end nodes are in the graph
    if start not in graph or end not in graph:
        print("Invalid start or end location.")
        return

    # Start timing
    s_t = time.perf_counter()

    # Run the selected algorithm
    dist, path = algo(graph, start, end)

    # End timing
    e_t = time.perf_counter()

    if path is None:
        print("No path found.")
        return

    # Plot the path on the graph
    plot_path(graph, path)

    # Display the execution time and distance
    plot_exec_time(s_t, e_t)
    plot_dist(dist)

    plt.show()

def clear_textboxes(event):
    start_textbox.set_val('')
    end_textbox.set_val('')


def plot_map_with_osm_background():
    # Convert the graph to Web Mercator projection for compatibility with map tiles
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(csuf_campus_map)
    gdf_nodes = gdf_nodes.to_crs(epsg=3857)
    gdf_edges = gdf_edges.to_crs(epsg=3857)

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the edges and nodes on top of the OpenStreetMap tiles
    gdf_edges.plot(ax=ax, linewidth=1, edgecolor='blue')
    gdf_nodes.plot(ax=ax, markersize=8, color='red')

    # Add OpenStreetMap tiles as the background
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    # Set title and labels
    ax.set_title("Cal State Fullerton")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Return fig and ax for further customization (hover, GUI)
    return fig, ax


def plot_campus_map_with_nodes():
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

def plot_map():
    # Plot the campus map using osmnx, with custom colors for edges and nodes
    fig, ax = ox.plot_graph(
        csuf_campus_map,
        bgcolor='white',              # Background color
        node_size=0,                  # Hide default nodes
        edge_color='blue',            # Set edge color
        edge_linewidth=0.7,           # Edge line width
        show=False,                   # Prevent automatic show
        close=False                   # Keep plot open for additional layers
    )

    # Plot only the csuf_locations nodes
    for location, coords in csuf_locations.items():
        long, lat = coords[1], coords[0]
        ax.plot(long, lat, 'ro', markersize=8)  # Red markers for locations

    plt.title("Cal State Fullerton Campus Map with Nodes")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Return figure and axis for further customization
    return fig, ax


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


def plot_path(graph, path):
    plot_map()

    start_y, start_x = graph[path[0]]['coords']
    end_y, end_x = graph[path[-1]]['coords']
    coords_x = []
    coords_y = []
    for node in path:
        y, x = graph[node]['coords']
        coords_x.append(x)
        coords_y.append(y)

    plt.plot(coords_x, coords_y, '.y-', lw=2)
    plt.plot(start_x, start_y, 'go', markersize=10)
    plt.plot(end_x, end_y, 'bo', markersize=10)

    plt.annotate('Start', (start_x, start_y), textcoords="offset points", xytext=(-20, -20), ha='center', color='black',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=2))
    plt.annotate('End', (end_x, end_y), textcoords="offset points", xytext=(-20, -20), ha='center', color='black',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", lw=2))


def plot_location_names(event):
    plt.figure()
    plt.title('')

    text = []
    for location in csuf_locations.keys():
        text.append(f"{location}\n")

    plt.text(0.3, 0.1, ''.join(text), fontsize=10, color='black', transform=plt.gca().transAxes)
    plt.axis('off')
    plt.show()

def clear_textboxes(event):
    start_textbox.set_val('')
    end_textbox.set_val('')

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

