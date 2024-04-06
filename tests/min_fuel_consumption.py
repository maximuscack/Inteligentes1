from collections import deque
import os
import random
from networkx import MultiDiGraph
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
import heapq
import random

CIUDAD_MANIZALES_GRAPHML = 'app/data/mapas/manizales.graphml'

G: MultiDiGraph

# Verificar si el archivo GraphML existe
if os.path.exists(CIUDAD_MANIZALES_GRAPHML):
    # Cargar el gráfico desde el archivo GraphML
    G = ox.load_graphml(CIUDAD_MANIZALES_GRAPHML)
else:
    # Obtener el gráfico de la ciudad de Manizales desde OpenStreetMap
    G = ox.graph_from_place('Manizales, Colombia', network_type='all')
    # Guardar el gráfico en formato GraphML
    ox.save_graphml(G, filepath=CIUDAD_MANIZALES_GRAPHML)


'''
Importing and cleaning the map
'''


for edge in G.edges:
    # Cleaning the 'maxspeed' attribute, some values are lists, some are strings, some are None
    maxspeed = 40
    if 'maxspeed' in G.edges[edge]:
        maxspeed = G.edges[edge]['maxspeed']
        if isinstance(maxspeed, list):
            print('list?!', maxspeed)
            speeds = [int(speed) for speed in maxspeed]
            maxspeed = min(speeds)
        elif isinstance(maxspeed, str):
            maxspeed = int(maxspeed)
    G.edges[edge]['maxspeed'] = maxspeed
    # Adding the 'weight' attribute (time = distance / speed)
    G.edges[edge]['weight'] = G.edges[edge]['length'] / maxspeed




'''
Útiles visuales
'''


def style_unvisited_edge(edge):
    G.edges[edge]['color'] = '#d36206'
    G.edges[edge]['alpha'] = 0.2
    G.edges[edge]['linewidth'] = 0.5


def style_visited_edge(edge):
    G.edges[edge]['color'] = '#d36206'
    G.edges[edge]['alpha'] = 1
    G.edges[edge]['linewidth'] = 1


def style_active_edge(edge):
    G.edges[edge]['color'] = '#e8a900'
    G.edges[edge]['alpha'] = 1
    G.edges[edge]['linewidth'] = 1


def style_path_edge(edge):
    G.edges[edge]['color'] = 'white'
    G.edges[edge]['alpha'] = 1
    G.edges[edge]['linewidth'] = 1

#


def plot_graph():
    ox.plot_graph(
        G,
        node_size=[G.nodes[node]['size'] for node in G.nodes],
        edge_color=[G.edges[edge]['color'] for edge in G.edges],
        edge_alpha=[G.edges[edge]['alpha'] for edge in G.edges],
        edge_linewidth=[G.edges[edge]['linewidth'] for edge in G.edges],
        node_color=[G.nodes[node].get('node_color', '#e8a900') for node in G.nodes],
        bgcolor='#18080e'
    )

#


def plot_heatmap(algorithm):
    edge_colors = ox.plot.get_edge_colors_by_attr(
        G, f'{algorithm}_uses', cmap='hot')
    fig, _ = ox.plot_graph(
        G,
        node_size=0,
        edge_color=edge_colors,
        bgcolor='#18080e'
    )


'''
Implementación Algoritmos
'''


def dijkstra(orig, dest, plot=False):
    for node in G.nodes:
        G.nodes[node]['visited'] = False
        G.nodes[node]['distance'] = float('inf')
        G.nodes[node]['previous'] = None
        G.nodes[node]['size'] = 0
    for edge in G.edges:
        style_unvisited_edge(edge)
    G.nodes[orig]['distance'] = 0
    G.nodes[orig]['size'] = 50
    G.nodes[dest]['size'] = 50
    pq = [(0, orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                plot_graph()
            return
        if G.nodes[node]['visited']:
            continue
        G.nodes[node]['visited'] = True
        for edge in G.out_edges(node):
            style_visited_edge((edge[0], edge[1], 0))
            neighbor = edge[1]
            weight = G.edges[(edge[0], edge[1], 0)]['weight']
            if G.nodes[neighbor]['distance'] > G.nodes[node]['distance'] + weight:
                G.nodes[neighbor]['distance'] = G.nodes[node]['distance'] + weight
                G.nodes[neighbor]['previous'] = node
                heapq.heappush(pq, (G.nodes[neighbor]['distance'], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge((edge2[0], edge2[1], 0))
        step += 1


#

def distance(node1, node2):
    x1, y1 = G.nodes[node1]['x'], G.nodes[node1]['y']
    x2, y2 = G.nodes[node2]['x'], G.nodes[node2]['y']
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def a_star(orig, dest, plot=False):
    for node in G.nodes:
        G.nodes[node]['previous'] = None
        G.nodes[node]['size'] = 0
        G.nodes[node]['g_score'] = float('inf')
        G.nodes[node]['f_score'] = float('inf')
    for edge in G.edges:
        style_unvisited_edge(edge)
    G.nodes[orig]['size'] = 50
    G.nodes[dest]['size'] = 50
    G.nodes[orig]['g_score'] = 0
    G.nodes[orig]['f_score'] = distance(orig, dest)
    pq = [(G.nodes[orig]['f_score'], orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                plot_graph()
            return
        for edge in G.out_edges(node):
            style_visited_edge((edge[0], edge[1], 0))
            neighbor = edge[1]
            tentative_g_score = G.nodes[node]['g_score'] + \
                distance(node, neighbor)
            if tentative_g_score < G.nodes[neighbor]['g_score']:
                G.nodes[neighbor]['previous'] = node
                G.nodes[neighbor]['g_score'] = tentative_g_score
                G.nodes[neighbor]['f_score'] = tentative_g_score + \
                    distance(neighbor, dest)
                heapq.heappush(pq, (G.nodes[neighbor]['f_score'], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge((edge2[0], edge2[1], 0))
        step += 1


def reconstruct_path(orig, dest, plot=False, algorithm=None):
    for edge in G.edges:
        style_unvisited_edge(edge)
    dist = 0
    speeds = []
    curr = dest
    while curr != orig:
        prev = G.nodes[curr]['previous']
        dist += G.edges[(prev, curr, 0)]['length']
        speeds.append(G.edges[(prev, curr, 0)]['maxspeed'])
        style_path_edge((prev, curr, 0))
        if algorithm:
            G.edges[(prev, curr, 0)][f'{algorithm}_uses'] = G.edges[(
                prev, curr, 0)].get(f'{algorithm}_uses', 0) + 1
        curr = prev
    dist /= 1000
    if plot:
        print(f'Distance: {dist}')
        print(f'Avg. speed: {sum(speeds)/len(speeds)}')
        print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')
        plot_graph()


start = random.choice(list(G.nodes))
end = random.choice(list(G.nodes))

def dijkstra_min_fuel_consumption(orig, dest, vehicle_fuel_efficiency, plot=False):
    visited = set()  # Conjunto de nodos visitados
    total_fuel_consumed = 0  # Total de combustible consumido
    for node in G.nodes:
        G.nodes[node]['previous'] = None
        G.nodes[node]['size'] = 0
        G.nodes[node]['g_score'] = float('inf')
    for edge in G.edges(keys=True):
        style_unvisited_edge(edge)
    G.nodes[orig]['size'] = 50
    G.nodes[dest]['size'] = 50
    G.nodes[orig]['g_score'] = 0
    pq = [(0, orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                plot_graph()
            return reconstruct_path(orig, dest, plot=plot, algorithm='dijkstra_min_fuel_consumption'), total_fuel_consumed
        if node in visited:
            continue
        visited.add(node)
        for edge in G.out_edges(node, keys=True):
            style_visited_edge((edge[0], edge[1], edge[2]))
            neighbor = edge[1]
            edge_length = G.edges[edge]['length']
            max_speed = G.edges[edge]['maxspeed']
            fuel_consumption = edge_length / (max_speed * vehicle_fuel_efficiency)
            total_fuel_consumed += fuel_consumption
            tentative_g_score = G.nodes[node]['g_score'] + fuel_consumption
            if tentative_g_score < G.nodes[neighbor]['g_score']:
                G.nodes[neighbor]['previous'] = node
                G.nodes[neighbor]['g_score'] = tentative_g_score
                heapq.heappush(pq, (G.nodes[neighbor]['g_score'], neighbor))
                for edge2 in G.out_edges(neighbor, keys=True):
                    style_active_edge((edge2[0], edge2[1], edge2[2]))
                fuel_used = fuel_consumption * vehicle_fuel_efficiency
                print(f'Used {fuel_used:.2f} gallons of fuel for edge {edge}')
        print(f'total = {total_fuel_consumed:.2f} gallons')
    step += 1






dijkstra_min_fuel_consumption(start, end, 1000, plot=True)