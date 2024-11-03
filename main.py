import matplotlib
matplotlib.use("TkAgg")
from tkinter import ttk  # For Combobox dropdowns
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from graph import add_csuf_locations, create_graph, csuf_campus_map, add_locations, csuf_locations
from visualizer import plot_campus_map_with_nodes, plot_location_names, run_algo, clear_textboxes, on_hover
from algorithms import BFS, DFS, Dijkstra

# Set the coordinates for CSUF
Latitude = 33.88534
Longitude = -117.88742

def main():
    # Step 1: Add custom locations to the map
    add_csuf_locations()

    # Step 2: Plot the map with only campus nodes and background
    fig, ax, campus_locations = plot_campus_map_with_nodes()

    # Step 3: Create the graph and add locations
    graph = create_graph(csuf_campus_map)
    add_locations(graph)
    on_hover(fig, ax, csuf_locations)  # Enables hover functionality

    # Step 4: Set up the dropdowns using tkinter's Combobox
    root = fig.canvas.manager.window
    tk_frame = tk.Frame(root)
    tk_frame.pack(side=tk.BOTTOM, fill=tk.X)

    location_options = list(csuf_locations.keys())

    start_label = tk.Label(tk_frame, text="Start:")
    start_label.pack(side=tk.LEFT)
    start_dropdown = ttk.Combobox(tk_frame, values=location_options)
    start_dropdown.pack(side=tk.LEFT)

    end_label = tk.Label(tk_frame, text="End:")
    end_label.pack(side=tk.LEFT)
    end_dropdown = ttk.Combobox(tk_frame, values=location_options)
    end_dropdown.pack(side=tk.LEFT)

    # Step 5: Set up buttons using matplotlib widgets for the algorithms
    bfs_ax = plt.axes([0.625, 0.005, 0.11, 0.1])
    dfs_ax = plt.axes([0.75, 0.005, 0.11, 0.1])
    dijkstra_ax = plt.axes([0.875, 0.005, 0.11, 0.1])
    #clear_ax = plt.axes([0.075, 0.01, 0.2, 0.03])
    show_locations_ax = plt.axes([0.35, 0.01, 0.2, 0.03])

    # Button actions for each algorithm using selected dropdown values
    bfs_button = Button(bfs_ax, 'Run BFS')
    bfs_button.on_clicked(lambda event: run_algo(graph, BFS, start_dropdown.get(), end_dropdown.get()))

    dfs_button = Button(dfs_ax, 'Run DFS')
    dfs_button.on_clicked(lambda event: run_algo(graph, DFS, start_dropdown.get(), end_dropdown.get()))

    dijkstra_button = Button(dijkstra_ax, 'Run Dijkstras')
    dijkstra_button.on_clicked(lambda event: run_algo(graph, Dijkstra, start_dropdown.get(), end_dropdown.get()))

    # Clear and show location buttons
    #clear_button = Button(clear_ax, 'Clear')
    #clear_button.on_clicked(clear_textboxes)

    show_locations_button = Button(show_locations_ax, 'Location Names')
    show_locations_button.on_clicked(plot_location_names)

    # Display the plot
    plt.show()


# Run the main function only if this script is executed directly
if __name__ == "__main__":
    main()
