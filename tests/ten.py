import os
import heapq
import folium
import imageio
import osmnx as ox
import streamlit as st
import matplotlib.pyplot as plt
from networkx import MultiDiGraph
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


def cargar_graficos(barrios):
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


def inicializar_mapa(barrio_selec, graficos):
    indice_barrio = barrios.index(barrio_selec)
    graph = graficos[indice_barrio]
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


def graficar_mapa(mapa):
    st.write('Mapa:')
    folium_static(mapa)


def style_unvisited_edge(graph, edge):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 0.2
    graph.edges[edge]['linewidth'] = 0.5


def style_visited_edge(graph, edge, step):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 0.2
    graph.edges[edge]['linewidth'] = 0.5
    plot_graph(graph, step)


def style_active_edge(graph, edge, step):
    graph.edges[edge]['color'] = '#e8a900'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1
    plot_graph(graph, step)


def style_path_edge(graph, edge, step):
    graph.edges[edge]['color'] = 'white'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1
    plot_graph(graph, step)


def plot_graph(graph, step):
    fig, ax = plt.subplots(figsize=(10, 10))
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
    ax.set_title(f'Step {step}')
    ax.set_axis_off()
    plt.savefig(os.path.join(IMAGES_DIR, f'image_{step}.png'))
    plt.close(fig)


def limpiar_carpeta():
    files = os.listdir(IMAGES_DIR)
    for file in files:
        os.remove(os.path.join(IMAGES_DIR, file))


def distance(graph, node1, node2):
    x1, y1 = graph.nodes[node1]['x'], graph.nodes[node1]['y']
    x2, y2 = graph.nodes[node2]['x'], graph.nodes[node2]['y']
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def a_star(graph, origen, destino, plot=False):
    step = 0
    for node in graph.nodes:
        graph.nodes[node]['previous'] = None
        graph.nodes[node]['size'] = 0
        graph.nodes[node]['g_score'] = float('inf')
        graph.nodes[node]['f_score'] = float('inf')
    for edge in graph.edges:
        style_unvisited_edge(graph, edge)
    graph.nodes[origen]['size'] = 50
    graph.nodes[destino]['size'] = 50
    graph.nodes[origen]['g_score'] = 0
    graph.nodes[origen]['f_score'] = distance(graph, origen, destino)
    pq = [(graph.nodes[origen]['f_score'], origen)]
    while pq:
        _, node = heapq.heappop(pq)
        if node == destino:
            if plot:
                print('Iteraciones:', step)
                plot_graph(graph, step)
            return
        for edge in graph.out_edges(node):
            # edge_with_key = (())  # Agregar el tercer elemento key
            # Pasar el borde con key a la función
            style_visited_edge(graph, (edge[0], edge[1], 0), step)
            neighbor = edge[1]
            tentative_g_score = graph.nodes[node]['g_score'] + \
                distance(graph, node, neighbor)
            if tentative_g_score < graph.nodes[neighbor]['g_score']:
                graph.nodes[neighbor]['previous'] = node
                graph.nodes[neighbor]['g_score'] = tentative_g_score
                graph.nodes[neighbor]['f_score'] = tentative_g_score + \
                    distance(graph, neighbor, destino)
                heapq.heappush(
                    pq, (graph.nodes[neighbor]['f_score'], neighbor))
                for edge2 in graph.out_edges(neighbor):
                    style_active_edge(graph, (edge2[0], edge2[1], 0), step)
        step += 1
    if plot:
        plot_graph(graph, step)


def reconstruct_path(graph, origen, destino, plot=False, algorithm=None):
    for edge in graph.edges:
        style_unvisited_edge(graph, edge)
    dist = 0
    speeds = []
    curr = destino
    step = 0
    while curr != origen:
        prev = graph.nodes[curr]['previous']
        dist += graph.edges[(prev, curr, 0)]['length']
        speeds.append(graph.edges[(prev, curr, 0)]['maxspeed'])
        style_path_edge(graph, (prev, curr, 0), step)
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
        plot_graph(graph, step)


def main():
    graficos = cargar_graficos(barrios)

    st.title('Selecciona un barrio para mostrar su gráfico:')
    barrio_selec = st.selectbox('Barrios', barrios)

    mapa, graph = inicializar_mapa(barrio_selec, graficos)

    for edge in graph.edges:
        maxspeed = 40
        if 'maxspeed' in graph.edges[edge]:
            maxspeed = graph.edges[edge]['maxspeed']
            if isinstance(maxspeed, list):
                speeds = [int(speed) for speed in maxspeed]
                maxspeed = min(speeds)
            elif isinstance(maxspeed, str):
                maxspeed = int(maxspeed)
        graph.edges[edge]['maxspeed'] = maxspeed

        graph.edges[edge]['time'] = graph.edges[edge]['length'] / maxspeed

    graficar_mapa(mapa)

    st.title('Encuentra tu ruta')
    col1, col2 = st.columns(2)

    with col1:
        origen = st.text_input('Origen', '')
    with col2:
        destino = st.text_input('Destino', '')

    if origen != '' and destino != '' and st.button('Hallar ruta'):

        limpiar_carpeta()

        origen = int(origen)
        destino = int(destino)
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
                print(f"Error: No se pudo encontrar el archivo {filename}")

        if images:
            imageio.mimsave(os.path.join(
                IMAGES_DIR, 'animation.gif'), images, fps=3)
            st.image(os.path.join(IMAGES_DIR, 'animation.gif'))
        else:
            print("Error: No hay imágenes para crear la animación")


if __name__ == '__main__':
    main()
