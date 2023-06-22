import os
import webbrowser
import pandas as pd
import numpy as np
from itertools import permutations
from scipy.spatial import distance_matrix
import plotly.graph_objects as go
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def load_dataset():
    global df
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return
    df = pd.read_csv(filepath, header=None, names=['city', 'x', 'y'])
    start_entry.config(state='normal')
    run_button.config(state='normal')
    export_button.config(state='normal')

def export_dataset():
    if route:
        df_route = pd.DataFrame(route, columns=["city", "x", "y"])
        filepath = filedialog.asksaveasfilename(defaultextension=".csv")
        if not filepath:
            return
        df_route.to_csv(filepath, index=False, header=False)

def run_tsp_brute_force():
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

    cities = list(df['city'])
    if current_city in cities: 
        cities.remove(current_city)
    cities.insert(0, current_city)  # Ensure we start at the current city

    shortest_distance = float('inf')
    best_route = None

    for city_order in permutations(cities):
        route_distance = sum(dist_matrix.loc[city_order[i-1]][city_order[i]] for i in range(len(city_order)))
        if route_distance < shortest_distance:
            shortest_distance = route_distance
            best_route = city_order

    route = [(city, df.loc[df['city'] == city, 'x'].item(), df.loc[df['city'] == city, 'y'].item()) for city in best_route]
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += np.sqrt((route[i][1] - route[i + 1][1]) ** 2 + (route[i][2] - route[i + 1][2]) ** 2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['x'],
        y=df['y'],
        mode='markers+text',
        text=df['city'],
        textposition='top center'
    ))
    fig.add_trace(go.Scatter(
        x=[r[1] for r in route],
        y=[r[2] for r in route],
        mode='lines',
        line=dict(color='royalblue', width=2),
    ))
    fig.add_trace(go.Scatter(
        x=[route[0][1], route[-1][1]],
        y=[route[0][2], route[-1][2]],
        mode='markers',
        marker=dict(size=12, color=['green', 'red']),
    ))
    fig.update_layout(
        title=f"Brute force method - Total Distance: {total_distance:.2f}",
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

root = tk.Tk()
root.title("TSP Solver")
df = None
route = None
load_button = tk.Button(root, text="Load Dataset", command=load_dataset)
load_button.pack()
start_entry = tk.Entry(root, state='disabled')
start_entry.pack()
run_button = tk.Button(root, text="Run TSP", state='disabled', command=run_tsp_brute_force)
run_button.pack()
export_button = tk.Button(root, text="Export Route", state='disabled', command=export_dataset)
export_button.pack()
root.mainloop()
