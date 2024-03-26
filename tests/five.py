import os
import heapq
import folium
import osmnx as ox
import streamlit as st
import matplotlib.pyplot as plt
from networkx import MultiDiGraph
from streamlit_folium import folium_static

CIUDAD_MANIZALES_DIR = 'app/data/mapas/'

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
graph = graficos[indice_barrio]

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
    st.write(f'Ruta encontrada: {origen} -> {destino}')

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


def plot_graph(graph, ax=None):
    fig, ax = ox.plot_graph(graph, ax=ax, show=False, close=False,
                            edge_color='gray', edge_alpha=0.8, node_color='blue', node_size=30)
    return fig, ax


def distance(node1, node2):
    x1, y1 = barrio_selec.nodes[node1]['x'], barrio_selec.nodes[node1]['y']
    x2, y2 = barrio_selec.nodes[node2]['x'], barrio_selec.nodes[node2]['y']
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def a_star(orig, dest, G: MultiDiGraph, plot=False):
    images = []
    for node in G.nodes:
        G.nodes[node]['previous'] = None
        G.nodes[node]['size'] = 0
        G.nodes[node]['g_score'] = float('inf')
        G.nodes[node]['f_score'] = float('inf')
    for edge in G.edges:
        G.edges[edge]['style'] = 'unvisited'
    G.nodes[orig]['size'] = 50
    G.nodes[dest]['size'] = 50
    G.nodes[orig]['g_score'] = 0
    G.nodes[orig]['f_score'] = distance(orig, dest)
    pq = [(G.nodes[orig]['f_score'], orig)]
    step = 0
    while pq:
        fig, _ = plot_graph(G)
        images.append(fig)
        plt.close(fig)

        _, node = heapq.heappop(pq)
        if node == dest:
            if plot:
                print('Iteraciones:', step)
                st.pyplot(images)
            return
        for edge in G.out_edges(node):
            G.edges[edge]['style'] = 'visited'
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
                    G.edges[edge2]['style'] = 'active'
        step += 1


def reconstruct_path(orig, dest, G: MultiDiGraph, plot=False, algorithm=None):
    images = []
    for edge in G.edges:
        G.edges[edge]['style'] = 'unvisited'
    dist = 0
    speeds = []
    curr = dest
    while curr != orig:
        prev = G.nodes[curr]['previous']
        dist += G.edges[(prev, curr, 0)]['length']
        speeds.append(G.edges[(prev, curr, 0)]['maxspeed'])
        G.edges[(prev, curr, 0)]['style'] = 'path'
        if algorithm:
            G.edges[(prev, curr, 0)][f'{algorithm}_uses'] \
                = G.edges[(prev, curr, 0)].get(f'{algorithm}_uses', 0) + 1
        curr = prev
        fig, _ = plot_graph(G)
        images.append(fig)
        plt.close(fig)
    dist /= 1000
    if plot:
        print(f'Distance: {dist}')
        print(f'Avg. speed: {sum(speeds)/len(speeds)}')
        print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')
        st.pyplot(images)
