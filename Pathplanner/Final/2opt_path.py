import os
import webbrowser
import pandas as pd
import numpy as np
import networkx as nx
import tkinter as tk
from tkinter import filedialog, messagebox
from itertools import combinations
from scipy.spatial import distance_matrix
import plotly.graph_objects as go
from tkinter import ttk

def load_dataset():
    global df
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return
    df = pd.read_csv(filepath, header=None, names=['city', 'x', 'y'])
    start_entry.config(state='normal')
    run_button.config(state='normal')
    export_button.config(state='normal')
    progress['maximum'] = 50  # The number of iterations in your TSP calculation

def export_dataset():
    if route:
        df_route = pd.DataFrame(route[:-1], columns=["city", "x", "y"])  # Exclude the last point
        filepath = filedialog.asksaveasfilename(defaultextension=".csv")
        if not filepath:
            return
        df_route.to_csv(filepath, index=False, header=False)

def run_tsp():
    global df
    global route
    current_city = start_entry.get()
    if current_city == '':
        current_city = df.iloc[0]['city']
    elif current_city not in df['city'].values:
        messagebox.showerror("Error", "Invalid Point. Make sure it's one of the Points in the dataset.")
        return
    distances = distance_matrix(df[['x', 'y']].values, df[['x', 'y']].values)
    dist_matrix = pd.DataFrame(distances, index=df.city, columns=df.city)
    G = nx.from_numpy_array(dist_matrix.values.astype(float))
    source_index = df[df['city'] == current_city].index[0]
    tsp_route = nx.approximation.greedy_tsp(G, source=source_index)
    progress['value'] = 0
    for _ in range(50):
        progress['value'] += 1  # Update the progress bar
        root.update_idletasks()
        for i, j in combinations(range(1, len(tsp_route) - 1), 2):
            if i != j:
                new_route = tsp_route[:i] + tsp_route[i:j][::-1] + tsp_route[j:]
                if sum(dist_matrix.values[new_route[i], new_route[i - 1]] for i in range(1, len(new_route))) < sum(
                        dist_matrix.values[tsp_route[i], tsp_route[i - 1]] for i in range(1, len(tsp_route))):
                    tsp_route = new_route
    route = [(df.iloc[i]['city'], df.iloc[i]['x'], df.iloc[i]['y']) for i in tsp_route]
    route_one_way = route[:-1]
    total_distance = 0
    for i in range(len(route_one_way) - 1):
        total_distance += np.sqrt((route_one_way[i][1] - route_one_way[i + 1][1]) ** 2 + (route_one_way[i][2] - route_one_way[i + 1][2]) ** 2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['x'],
        y=df['y'],
        mode='markers+text',
        text=df['city'],
        textposition='top center'
    ))
    fig.add_trace(go.Scatter(
        x=[r[1] for r in route_one_way],
        y=[r[2] for r in route_one_way],
        mode='lines',
        line=dict(color='royalblue', width=2),
    ))
    fig.add_trace(go.Scatter(
        x=[route_one_way[0][1], route_one_way[-1][1]],
        y=[route_one_way[0][2], route_one_way[-1][2]],
        mode='markers',
        marker=dict(size=12, color=['green', 'red']),
    ))
    fig.update_layout(
        title=f"2opt method - Total Distance: {total_distance:.2f}",
        xaxis_title="X",
        yaxis_title="Y",
        autosize=False,
        width=1500,
        height=800,
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        showlegend=False,
    )
    fig.write_html("plot.html")
    webbrowser.open('file://' + os.path.realpath("plot.html"))
    progress['value'] = 0

root = tk.Tk()
root.title("TSP Solver")
df = None
route = None
load_button = tk.Button(root, text="Load Dataset", command=load_dataset)
load_button.pack()
start_entry = tk.Entry(root, state='disabled')
start_entry.pack()
run_button = tk.Button(root, text="Run TSP", state='disabled', command=run_tsp)
run_button.pack()
export_button = tk.Button(root, text="Export Route", state='disabled', command=export_dataset)
export_button.pack()
progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress.pack()
root.mainloop()