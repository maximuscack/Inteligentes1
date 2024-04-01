import os
from matplotlib import pyplot as plt
import networkx as nx
from networkx import MultiDiGraph
import osmnx as ox
import random
import heapq

CIUDAD_MANIZALES_DIR = 'app/data/mapas/'


barrio = 'Comuna Cumanday'
filepath = os.path.join(CIUDAD_MANIZALES_DIR, f'{barrio}.graphml')

G: MultiDiGraph = MultiDiGraph()

if os.path.exists(filepath):
    G = ox.load_graphml(filepath)
else:
    place_name = f'{barrio}, Caldas, Colombia'
    G = ox.graph_from_place(place_name, network_type='drive')
    ox.save_graphml(G, filepath=filepath)


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
    G.edges[edge]['weight'] = G.edges[edge]['length'] / maxspeed


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


def plot_graph():
    ox.plot_graph(
        G,
        node_size=[G.nodes[node]['size'] for node in G.nodes],
        edge_color=[G.edges[edge]['color'] for edge in G.edges],
        edge_alpha=[G.edges[edge]['alpha'] for edge in G.edges],
        edge_linewidth=[G.edges[edge]['linewidth'] for edge in G.edges],
        node_color='white',
        bgcolor='#18080e'
    )


# def plot_heatmap(algorithm: str):
#     edge_colors = [G.edges[edge][f'{algorithm}_uses']
#                    for edge in G.edges()]
#     fig, ax = ox.plot_graph(G, node_size=0, edge_color=edge_colors,
#                             bgcolor='#18080e', show=False, close=False)
#     cmap = plt.get_cmap('hot')
#     nx.draw_networkx_edges(G, pos=ox.plot_graph(G, node_size=0, edge_color='gray', bgcolor='#18080e',
#                            show=False, close=False)[1], edge_color=edge_colors, edge_cmap=cmap, ax=ax)

#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(
#         vmin=min(edge_colors), vmax=max(edge_colors)))
#     sm.set_array([])
#     plt.colorbar(sm)
#     plt.show()


'''
'''


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


'''
'''


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


''''''

start = random.choice(list(G.nodes))
end = random.choice(list(G.nodes))

a_star(start, end, plot=True)
# reconstruct_path(start, end, plot=True)


# plot_heatmap('a_star')
