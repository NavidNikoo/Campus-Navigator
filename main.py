import matplotlib
matplotlib.use("TkAgg")  # Set TkAgg as the backend for tkinter integration
from tkinter import ttk  # For Combobox dropdowns
import tkinter as tk  # GUI library for dropdowns and labels
import matplotlib.pyplot as plt  # Plotting library
from matplotlib.widgets import Button  # For algorithm buttons on the map
from graph import add_csuf_locations, create_graph, csuf_campus_map, add_locations, csuf_locations  # Graph functions and data
from visualizer import plot_campus, run_algo, on_hover  # Visualization functions
from algorithms import BFS, DFS, Dijkstra  # Pathfinding algorithms

def main():
    """
    Main function to run the CSUF campus navigation program. It initializes the map, sets up the graph with custom
    locations, configures the GUI for selecting start and end points, and creates buttons for running algorithms.
    """
    # Step 1: Add custom CSUF-specific locations to the map graph
    add_csuf_locations()

    # Step 2: Plot the campus map with only the main nodes (locations) and background
    fig, ax, campus_locations = plot_campus()

    # Step 3: Create the graph structure from the map and add custom locations
    graph = create_graph(csuf_campus_map)  # Converts the map to a graph structure
    add_locations(graph)  # Adds custom locations (like buildings) to the graph
    on_hover(fig, ax, csuf_locations)  # Enables hover functionality for node names

    # Step 4: Set up the dropdowns using tkinter's Combobox
    root = fig.canvas.manager.window  # Access the tkinter root window
    tk_frame = tk.Frame(root)  # Create a frame to hold dropdowns and labels
    tk_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Position the frame at the bottom of the window

    # Define location options based on the csuf_locations dictionary
    location_options = list(csuf_locations.keys())

    # Create and pack the start location label and dropdown
    start_label = tk.Label(tk_frame, text="Start:")
    start_label.pack(side=tk.LEFT)
    start_dropdown = ttk.Combobox(tk_frame, values=location_options)
    start_dropdown.pack(side=tk.LEFT)

    # Create and pack the end location label and dropdown
    end_label = tk.Label(tk_frame, text="End:")
    end_label.pack(side=tk.LEFT)
    end_dropdown = ttk.Combobox(tk_frame, values=location_options)
    end_dropdown.pack(side=tk.LEFT)

    # Step 5: Set up buttons using matplotlib widgets for the algorithms
    bfs_ax = plt.axes([0.0350, 0.005, 0.11, 0.1])  # Define position for BFS button
    dfs_ax = plt.axes([0.155, 0.005, 0.11, 0.1])   # Define position for DFS button
    dijkstra_ax = plt.axes([0.275, 0.005, 0.11, 0.1])  # Define position for Dijkstra's button

    # Button actions for each algorithm using selected dropdown values
    bfs_button = Button(bfs_ax, 'Run BFS')
    bfs_button.on_clicked(lambda event: run_algo(graph, BFS, start_dropdown.get(), end_dropdown.get(), fig, ax))

    dfs_button = Button(dfs_ax, 'Run DFS')
    dfs_button.on_clicked(lambda event: run_algo(graph, DFS, start_dropdown.get(), end_dropdown.get(), fig, ax))

    dijkstra_button = Button(dijkstra_ax, 'Run Dijkstras')
    dijkstra_button.on_clicked(lambda event: run_algo(graph, Dijkstra, start_dropdown.get(), end_dropdown.get(), fig, ax))

    # Display the plot, integrating the matplotlib plot with tkinter widgets
    plt.show()

# Run the main function when this script is executed
if __name__ == "__main__":
    main()
