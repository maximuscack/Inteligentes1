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

# Lista para almacenar los gráficos de los barrios


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


graficos = cargar_graficos()

# Configurar la interfaz de usuario con Streamlit
st.title('Selecciona un barrio para mostrar su gráfico:')
barrio_selec = st.selectbox('Barrios', barrios)

# Obtener el índice del barrio seleccionado
indice_barrio = barrios.index(barrio_selec)

# Obtener el gráfico del barrio seleccionado
graph: MultiDiGraph = graficos[indice_barrio]


# Crear un mapa interactivo con Folium centrado en el barrio seleccionado
for node in graph.nodes:
    node_data = graph.nodes[node]
    if 'y' in node_data and 'x' in node_data:
        lat, lon = node_data['y'], node_data['x']
        break

mapa = folium.Map(location=[lat, lon], zoom_start=15,
                  control_scale=True, zoom_control=False)

# Añadir los nodos del gráfico al mapa
for nodo, data in graph.nodes(data=True):
    folium.Marker(location=(data['y'], data['x']),
                  popup=str(nodo)).add_to(mapa)

# Mostrar el mapa interactivo
st.write(f'Mapa de {barrio_selec}:')
folium_static(mapa)

graficos = cargar_graficos()

''' ALGORITMO '''

for edge in graph.edges:
    # Cleaning the 'maxspeed' attribute, some values are lists, some are strings, some are None
    maxspeed = 40
    if 'maxspeed' in graph.edges[edge]:
        maxspeed = graph.edges[edge]['maxspeed']
        if isinstance(maxspeed, list):
            speeds = [int(speed) for speed in maxspeed]
            maxspeed = min(speeds)
        elif isinstance(maxspeed, str):
            maxspeed = int(maxspeed)
    graph.edges[edge]['maxspeed'] = maxspeed
    # Adding the 'weight' attribute (time = distance / speed)
    graph.edges[edge]['time'] = graph.edges[edge]['length'] / maxspeed

for node in graph.nodes:
    position = (graph.nodes[node]['x'], graph.nodes[node]['y'])
    graph.nodes[node]['pos'] = position


def style_unvisited_edge(edge):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 0.2
    graph.edges[edge]['linewidth'] = 0.5


def style_visited_edge(edge):
    graph.edges[edge]['color'] = '#d36206'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1


def style_active_edge(edge):
    graph.edges[edge]['color'] = '#e8a900'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1


def style_path_edge(edge):
    graph.edges[edge]['color'] = 'white'
    graph.edges[edge]['alpha'] = 1
    graph.edges[edge]['linewidth'] = 1


def plot_graph(step):
    fig, ax = plt.subplots(figsize=(10, 10))
    ox.plot_graph(graph, ax=ax, node_size=0, edge_color='gray',
                  edge_linewidth=0.5, bgcolor='black')
    ax.set_title(f'Iteración {step}')
    ax.set_axis_off()
    plt.savefig(os.path.join(IMAGES_DIR, f'image_{step}.png'))
    plt.close(fig)

#


def plot_heatmap(algorithm):
    edge_colors = ox.plot.get_edge_colors_by_attr(
        graph, f'{algorithm}_uses', cmap='hot')
    _, _ = ox.plot_graph(
        graph,
        node_size=0,
        edge_color=edge_colors,
        bgcolor='#18080e'
    )


def distance(node1, node2):
    x1, y1 = graph.nodes[node1]['x'], graph.nodes[node1]['y']
    x2, y2 = graph.nodes[node2]['x'], graph.nodes[node2]['y']
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def a_star(orig, dest, plot=False):
    for node in graph.nodes:
        graph.nodes[node]['previous'] = None
        graph.nodes[node]['size'] = 0
        graph.nodes[node]['g_score'] = float('inf')
        graph.nodes[node]['f_score'] = float('inf')
    for edge in graph.edges:
        style_unvisited_edge(edge)
    graph.nodes[orig]['size'] = 50
    graph.nodes[dest]['size'] = 50
    graph.nodes[orig]['g_score'] = 0
    graph.nodes[orig]['f_score'] = distance(orig, dest)
    pq = [(graph.nodes[orig]['f_score'], orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                plot_graph(step)
            return
        for edge in graph.out_edges(node):
            style_visited_edge((edge[0], edge[1], 0))
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
                    style_active_edge((edge2[0], edge2[1], 0))
        step += 1


def reconstruct_path(orig, dest, plot=False, algorithm=None):
    for edge in graph.edges:
        style_unvisited_edge(edge)
    dist = 0
    speeds = []
    curr = dest
    step = 0  # Agrega esta línea para inicializar la variable 'step'
    while curr != orig:
        prev = graph.nodes[curr]['previous']
        dist += graph.edges[(prev, curr, 0)]['length']
        speeds.append(graph.edges[(prev, curr, 0)]['maxspeed'])
        style_path_edge((prev, curr, 0))
        if algorithm:
            graph.edges[(prev, curr, 0)][f'{algorithm}_uses'] \
                = graph.edges[(prev, curr, 0)].get(f'{algorithm}_uses', 0) + 1
        curr = prev
        step += 1  # Incrementa 'step' en cada iteración
    dist /= 1000
    if plot:
        print(f'Distance: {dist}')
        print(f'Avg. speed: {sum(speeds)/len(speeds)}')
        print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')
        plot_graph(step)


''' ALGORITMO '''

''' Animación '''


def create_animation():
    # Crear una lista de nombres de archivos de imágenes
    image_files = [
        os.path.join(IMAGES_DIR, f'image_{i}.png')
        for i in range(1, len(os.listdir(IMAGES_DIR)) + 1)
    ]

    # Crear una animación a partir de las imágenes
    images = []
    for filename in image_files:
        images.append(imageio.imread(filename))
    imageio.mimsave(os.path.join(IMAGES_DIR, 'animation.gif'), images, fps=1)


''' Animación '''

st.title('Encuentra tu ruta')

# Crear dos campos de entrada
# Crear dos columnas para los inputs
col1, col2 = st.columns(2)

# Añadir un input en cada columna con estilos personalizados
with col1:
    origen = st.text_input('Origen', '')
with col2:
    destino = st.text_input('Destino', '')

# Crear un botón que se active cuando ambos campos estén llenos
if origen != '' and destino != '' and st.button('Hallar ruta'):
    origen = int(origen)
    destino = int(destino)
    a_star(origen, destino, plot=True)
    reconstruct_path(origen, destino, plot=True)

    # generate_images()
    # create_animation()
