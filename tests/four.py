from collections import deque
import os
import random
from networkx import MultiDiGraph
import networkx as nx
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
import heapq
import random

CIUDAD_MANIZALES_GRAPHML = 'app/data/mapas/manizales.graphml'
# Definir una carpeta para almacenar las imágenes
# IMAGES_DIR = 'app/data/images'
# os.makedirs(IMAGES_DIR, exist_ok=True)

G: MultiDiGraph
N: MultiDiGraph = nx.MultiDiGraph()

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
            speeds = [int(speed) for speed in maxspeed]
            maxspeed = min(speeds)
        elif isinstance(maxspeed, str):
            maxspeed = int(maxspeed)
    G.edges[edge]['maxspeed'] = maxspeed
    # Adding the 'weight' attribute (time = distance / speed)
    G.edges[edge]['time'] = G.edges[edge]['length'] / maxspeed

for node in G.nodes:
    position = (G.nodes[node]['x'], G.nodes[node]['y'])
    G.nodes[node]['pos'] = position

for node, attrs in G.nodes(data=True):
    N.add_node(node, **attrs)


def on_click(event):
    if event.button == 1 and event.inaxes is not None:
        x, y = event.xdata, event.ydata
        # Buscar el nodo más cercano a la posición clickeada
        min_dist = float('inf')
        selected_node = None
        for node, (ntx, ny) in nx.get_node_attributes(G, 'pos').items():
            dist = (x - ntx) ** 2 + (y - ny) ** 2
            if dist < min_dist:
                min_dist = dist
                selected_node = node
        if selected_node is not None:
            print(f'Nodo seleccionado: {selected_node}')


# Dibujar solo los nodos con detalles mínimos
plt.figure(figsize=(8, 6))
pos = nx.get_node_attributes(N, 'pos')
nx.draw_networkx_nodes(
    N, pos=pos, node_size=10, alpha=0.5,
    node_color='skyblue'
)
plt.title('Manizales')

# Registrar el manejador de eventos de clic
plt.gcf().canvas.mpl_connect('button_press_event', on_click)

plt.axis('off')  # Ocultar ejes
plt.show()


# nodos_df = ox.graph_to_gdfs(G, edges=False)






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

#a_star(start, end, plot=True)
#reconstruct_path(start, end, plot=True)

def add_node_sizes(default_size=10):
    '''
    Agrega el atributo 'size' a todos los nodos con un valor predeterminado.
    '''
    for node in G.nodes:
        if 'size' not in G.nodes[node]:
            G.nodes[node]['size'] = default_size

def style_traffic_lights(default_color='green', default_linewidth=1):
    '''
    Modifica el color de los nodos que representan semáforos y agrega el atributo 'color', 'alpha' y 'linewidth' a los bordes.
    '''
    for node, data in G.nodes(data=True):
        #! Editar estilos originales.

        if random.random() < 0.15:
            G.nodes[node]['semaforo_rojo'] = True
            G.nodes[node]['tiempo'] = 10
            G.nodes[node]['node_color'] = default_color

        if random.random() < 0.0125:
            G.nodes[node]['es_turistico'] = True
            G.nodes[node]['node_color'] = '#FA0AFA'

        # if 'traffic_light' in G.nodes[node]:
        #     print(G.nodes[node])

        # if G.nodes[node]['semaforo']:  # Verifica si el nodo tiene el atributo 'semaforo'
            # semaforo = data['semaforo']
            # if isinstance(semaforo, dict) and 'color' in semaforo:
            # G.nodes[node]['node_color'] = default_color  # Cambia el color del nodo según el atributo 'color' del semáforo

    for edge in G.edges:
        if 'color' not in G.edges[edge]:
            G.edges[edge]['color'] = '#d36206'  # Define un color predeterminado para los bordes
        if 'alpha' not in G.edges[edge]:
            G.edges[edge]['alpha'] = 1  # Define un valor predeterminado para la transparencia de los bordes
        if 'linewidth' not in G.edges[edge]:
            G.edges[edge]['linewidth'] = default_linewidth  # Define un ancho de línea predeterminado para los bordes


def a_star_traffic_lights(orig, dest, plot=False):
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
            return reconstruct_path(orig, dest, plot=plot, algorithm='a_star_traffic_lights')
        for edge in G.out_edges(node):
            style_visited_edge((edge[0], edge[1], 0))
            neighbor = edge[1]
            tentative_g_score = G.nodes[node]['g_score'] + \
                distance(node, neighbor)
            travel_time = G.edges[(node, neighbor, 0)]['weight']  # considera el tiempo de viaje en función de la distancia y la velocidad máxima
            # Añade el tiempo de espera en semáforos al tiempo de viaje
            travel_time += G.edges[(node, neighbor, 0)].get('traffic_light_wait', 0)
            tentative_g_score += G.edges[(node, neighbor, 0)].get('traffic_light_wait', 0)
            if tentative_g_score < G.nodes[neighbor]['g_score']:
                G.nodes[neighbor]['previous'] = node
                G.nodes[neighbor]['g_score'] = tentative_g_score
                G.nodes[neighbor]['f_score'] = tentative_g_score + \
                    distance(neighbor, dest)
                heapq.heappush(pq, (G.nodes[neighbor]['f_score'], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge((edge2[0], edge2[1], 0))
        step += 1

# Antes de trazar el grafo, asegúrate de que todos los nodos tengan el atributo 'size' definido
add_node_sizes()
style_traffic_lights()


# Trama el grafo
plot_graph()

#a_star_traffic_lights(start, end, plot=True)
#--------------------------------------------------------------------------------


