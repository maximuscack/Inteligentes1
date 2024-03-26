import os
import heapq
import folium
import imageio
import osmnx as ox
import streamlit as st
import matplotlib.pyplot as plt
from networkx import MultiDiGraph
from networkx.classes.reportviews import OutMultiEdgeView
from streamlit_folium import folium_static

CIUDAD_MANIZALES_DIR = 'app/data/mapas/'
IMAGES_DIR = 'app/data/images'

barrios = [
    'Comuna Cumanday', 'Comuna La Macarena',
    'Comuna Palogrande', 'Comuna La Fuente',
    'Comuna San José', 'Comuna Nuevo Horizonte',
    'Comuna Atardeceres', 'Comuna Ciudadela del Norte',
    'Comuna Ecoturística Cerro de Oro', 'Comuna Universitaria',
]


@st.cache_data()
def cargar_graficos():
    graficos = []
    for barrio in barrios:
        filepath = os.path.join(CIUDAD_MANIZALES_DIR, f'{barrio}.graphml')
        if os.path.exists(filepath):
            graph = ox.load_graphml(filepath)
        else:
            place_name = f'{barrio}, Caldas, Colombia'
            graph = ox.graph_from_place(place_name, network_type='all')
            ox.save_graphml(graph, filepath=filepath)
        graficos.append(graph)
    return graficos


def inicializar_mapa(barrio_selec):
    indice_barrio = barrios.index(barrio_selec)
    graph = cargar_graficos()[indice_barrio]
    for node in graph.nodes:
        node_data = graph.nodes[node]
        if 'y' in node_data and 'x' in node_data:
            lat, lon = node_data['y'], node_data['x']
            break
    mapa = folium.Map(location=[lat, lon], zoom_start=15,
                      control_scale=True, zoom_control=False)
    for nodo, data in graph.nodes(data=True):
        folium.Marker(location=(data['y'], data['x']),
                      popup=str(nodo)).add_to(mapa)
    return mapa, graph


''' ALGORITMO '''


def plot_graphic(graph: MultiDiGraph, step: int):
    fig, ax = plt.subplots(figsize=(10, 10))

    print('arista:', [graph.edges[edge] for edge in graph.edges])
    ox.plot_graph(
        graph,
        node_size=[graph.nodes[node]['size'] for node in graph.nodes],
        edge_color=[graph.edges[edge]['color'] for edge in graph.edges],
        edge_alpha=[graph.edges[edge]['alpha'] for edge in graph.edges],
        edge_linewidth=[graph.edges[edge]['linewidth']
                        for edge in graph.edges],
        bgcolor='black',
        ax=ax
    )
    ax.set_title(f'Paso {step}')
    ax.set_axis_off()
    plt.savefig(os.path.join(IMAGES_DIR, f'image_{step}.png'))
    plt.close(fig)


# OutEdgeView, OutMultiEdgeView
def style_unvisited_edge(edge, graph: MultiDiGraph):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 0.2
    graph.edges[edge]['linewidth'] = 0.5


def style_visited_edge(edge, step, graph: MultiDiGraph):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 0.2
    graph.edges[edge]['linewidth'] = 0.5
    plot_graphic(graph, step)


def style_active_edge(edge, step, graph: MultiDiGraph):
    graph.edges[edge]['color'] = '#e8a900'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1
    plot_graphic(graph, step)


def style_path_edge(edge, step, graph: MultiDiGraph):
    graph.edges[edge]['color'] = 'white'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1
    plot_graphic(graph, step)


def plot_heatmap(algorithm):
    edge_colors = ox.plot.get_edge_colors_by_attr(
        graph, f'{algorithm}_uses', cmap='hot')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    ox.plot_graph(
        graph,
        ax=ax,
        node_size=0,
        edge_color=edge_colors,
        bgcolor='black',
    )
    ax.set_title(f'{algorithm} Heatmap')
    ax.set_axis_off()
    plt.savefig(os.path.join(IMAGES_DIR, f'{algorithm}_heatmap.png'))
    plt.close(fig)


def limpiar_carpeta():
    files = os.listdir(IMAGES_DIR)
    for file in files:
        os.remove(os.path.join(IMAGES_DIR, file))


def distance(node1, node2):
    x1, y1 = graph.nodes[node1]['x'], graph.nodes[node1]['y']
    x2, y2 = graph.nodes[node2]['x'], graph.nodes[node2]['y']
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def a_star(graph, orig, dest, plot=False):
    step = 0
    for node in graph.nodes:
        graph.nodes[node]['previous'] = None
        graph.nodes[node]['size'] = 0
        graph.nodes[node]['g_score'] = float('inf')
        graph.nodes[node]['f_score'] = float('inf')
    for edge in graph.edges:
        style_visited_edge(graph,edge, step)

    graph.nodes[orig]['size'] = 50
    graph.nodes[dest]['size'] = 50
    graph.nodes[orig]['g_score'] = 0
    graph.nodes[orig]['f_score'] = distance(orig, dest)
    pq = [(graph.nodes[orig]['f_score'], orig)]
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                plot_graphic(graph, step)
            return
        for edge in graph.out_edges(node):
            style_visited_edge(graph.edges[edge], step, graph)
            neighbor = edge[1]
            tentative_g_score = graph.nodes[node]['g_score'] + \
                distance(node, neighbor)
            if tentative_g_score < graph.nodes[neighbor]['g_score']:
                graph.nodes[neighbor]['previous'] = node
                graph.nodes[neighbor]['g_score'] = tentative_g_score
                graph.nodes[neighbor]['f_score'] = tentative_g_score + \
                    distance(neighbor, dest)
                heapq.heappush(
                    pq, (graph.nodes[neighbor]['f_score'], neighbor))
                for edge2 in graph.out_edges(neighbor):
                    style_active_edge(graph.edges[edge2], step, graph)
        step += 1

    if plot:
        plot_graphic(graph, step)


def reconstruct_path(graph: MultiDiGraph, orig, dest, plot=False, algorithm=None):
    for edge in graph.edges:
        style_unvisited_edge(graph.edges[edge], graph)
    dist = 0
    speeds = []
    curr = dest
    step = 0
    while curr != orig:
        prev = graph.nodes[curr]['previous']
        dist += graph.edges[(prev, curr, 0)]['length']
        speeds.append(graph.edges[(prev, curr, 0)]['maxspeed'])
        style_path_edge((prev, curr, 0), step, graph)
        if algorithm:
            graph.edges[(prev, curr, 0)][f'{algorithm}_uses'] \
                = graph.edges[(prev, curr, 0)].get(f'{algorithm}_uses', 0) + 1
        curr = prev
        step += 1
    dist /= 1000
    if plot:
        print(f'Distance: {dist}')
        print(f'Avg. speed: {sum(speeds)/len(speeds)}')
        print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')
        plot_graphic(graph, step)


''' ALGORITMO '''


if __name__ == '__main__':
    st.title('Selecciona un barrio para mostrar su gráfico:')
    barrio_selec = st.selectbox('Barrios', barrios)

    st.title('Encuentra tu ruta')
    col1, col2 = st.columns(2)
    with col1:
        origen = st.text_input('Origen', '')
    with col2:
        destino = st.text_input('Destino', '')

    if origen != '' and destino != '' and st.button('Hallar ruta'):

        files = os.listdir(IMAGES_DIR)
        for file in files:
            os.remove(os.path.join(IMAGES_DIR, file))

        origen = int(origen)
        destino = int(destino)
        mapa, graph = inicializar_mapa(barrio_selec)


        style_unvisited_edge(graph.edges, graph)
        
        a_star(graph, origen, destino, plot=True)
        reconstruct_path(graph, origen, destino, plot=True)

        image_files = [
            os.path.join(IMAGES_DIR, f'image_{i}.png')
            for i in range(1, len(os.listdir(IMAGES_DIR)) + 1)
        ]

        images = []
        for filename in image_files:
            if os.path.exists(filename):
                images.append(imageio.imread(filename))
            else:
                print(f'Error: No se pudo encontrar el archivo {filename}')

        if images:
            imageio.mimsave(os.path.join(
                IMAGES_DIR, 'animation.gif'), images, fps=3)
            st.image(os.path.join(IMAGES_DIR, 'animation.gif'))
        else:
            print('Error: No hay imágenes para crear la animación')

    mapa, graph = inicializar_mapa(barrio_selec)
    st.write(f'Mapa de {barrio_selec}:')
    folium_static(mapa)
