import os
import folium
import osmnx as ox
import streamlit as st
from networkx import MultiDiGraph

from app.data.constants import BARRIOS
from tests.eight import CIUDAD_MANIZALES_DIR


class Menu:
    ''' Class Menu is used to render to user. '''

    def __init__(self, graph: MultiDiGraph) -> None:
        pass

    def render(self):
        graficos = self.load_neighborhoods(BARRIOS)

        st.title('Selecciona un barrio para mostrar su gráfico:')
        barrio_selec = st.selectbox('Barrios', BARRIOS)

        mapa, graph = inicializar_mapa(barrio_selec, graficos)

        self.normalize_graph()

        def load_neighborhoods(self, neighborhoods) -> list[MultiDiGraph]:
            nets: list[MultiDiGraph] = []
            for neighbor in neighborhoods:
                filepath = os.path.join(
                    CIUDAD_MANIZALES_DIR, f'{neighbor}.graphml'
                )
                if os.path.exists(filepath):
                    graph: MultiDiGraph = ox.load_graphml(filepath)
                else:
                    place_name = f'{neighbor}, Caldas, Colombia'
                    graph: MultiDiGraph = ox.graph_from_place(
                        place_name, network_type='all'
                    )
                    ox.save_graphml(graph, filepath=filepath)
                nets.append(graph)
            return nets

    def inicializar_mapa(self, barrio_selec, graficos) -> tuple[folium.Map, MultiDiGraph]:
        indice_barrio: int = BARRIOS.index(barrio_selec)
        graph: MultiDiGraph = graficos[indice_barrio]
        for node in graph.nodes:
            lat, lon = (
                graph.nodes[node]['y'], graph.nodes[node]['x']
            )
            break
        mapa = folium.Map(
            location=[lat, lon],
            zoom_start=15.5,
            control_scale=True,
            zoom_control=True,
            prefer_canvas=True
        )
        for nodo, data in graph.nodes(data=True):
            folium.Marker(location=(data['y'], data['x']),
                          popup=str(nodo)).add_to(mapa)
        return mapa, graph

    def normalize_graph(self):
        print('NEED TO IMPLEMENT THIS FUNCTION')
