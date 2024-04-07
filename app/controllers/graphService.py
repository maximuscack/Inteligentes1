import os
import random
import folium
import streamlit as st
import osmnx as ox
from networkx import MultiDiGraph

from data.constants import (
    NOMBRES_BARRIOS, CIUDAD_MANIZALES_DIR
)


class GraphService:
    ''' Class GraphService is used to act over the graph. '''

    def __init__(self, graph: MultiDiGraph | None = None) -> None:
        self._G: MultiDiGraph = graph

    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph

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

    def load_neighbor_data(
        self, barrio_selec, graficos
    ) -> tuple[folium.Map, MultiDiGraph]:
        indice_barrio: int = NOMBRES_BARRIOS.index(barrio_selec)

        graph: MultiDiGraph = graficos[indice_barrio]

        for node in graph.nodes:
            lat, lon = (graph.nodes[node]['y'],
                        graph.nodes[node]['x'])
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

    def reset_graph(self):
        for edge in self._G.edges:
            maxspeed = 40
            if 'maxspeed' in self._G.edges[edge]:
                maxspeed = self._G.edges[edge]['maxspeed']
                if isinstance(maxspeed, list):
                    speeds = [int(speed) for speed in maxspeed]
                    maxspeed = min(speeds)
                elif isinstance(maxspeed, str):
                    maxspeed = int(maxspeed)

            self._G.edges[edge]['maxspeed'] = maxspeed
            self._G.edges[edge]['weight'] =\
                self._G.edges[edge]['length'] / maxspeed

            ''' From A* '''

            self._G.edges[edge]['color'] = '#d36206'
            self._G.edges[edge]['alpha'] = 0.2
            self._G.edges[edge]['linewidth'] = 0.5


        for node in self._G.nodes:
            self._G.nodes[node]['size'] = 10

            self._G.nodes[node]['semaforo_rojo'] = True
            self._G.nodes[node]['tiempo'] = 10

            if random.random() < 0.15:
                self._G.nodes[node]['tiempo'] = 10

                self._G.nodes[node]['semaforo_rojo'] = True
                self._G.nodes[node]['node_color'] = 'red'

                if random.random() < 0.5:
                    self._G.nodes[node]['semaforo_rojo'] = False
                    self._G.nodes[node]['node_color'] = 'green'

            if random.random() < 0.0125:
                self._G.nodes[node]['es_turistico'] = True
                self._G.nodes[node]['node_color'] = 'blue'


# def style_traffic_lights(default_color='green', default_linewidth=1):
#     '''
#     Modifica el color de los nodos que representan semáforos y agrega el atributo 'color', 'alpha' y 'linewidth' a los bordes.
#     '''
#     for node, data in G.nodes(data=True):
#         #! Editar estilos originales.

#         if random.random() < 0.15:
#             G.nodes[node]['semaforo_rojo'] = True
#             G.nodes[node]['tiempo'] = 10
#             G.nodes[node]['node_color'] = default_color

#         if random.random() < 0.0125:
#             G.nodes[node]['es_turistico'] = True
#             G.nodes[node]['node_color'] = '#FA0AFA'

        # if 'traffic_light' in G.nodes[node]:
        #     print(G.nodes[node])

        # if G.nodes[node]['semaforo']:  # Verifica si el nodo tiene el atributo 'semaforo'
            # semaforo = data['semaforo']
            # if isinstance(semaforo, dict) and 'color' in semaforo:
            # G.nodes[node]['node_color'] = default_color  # Cambia el color del nodo según el atributo 'color' del semáforo

    # for edge in G.edges:
    #     if 'color' not in G.edges[edge]:
    #         # Define un color predeterminado para los bordes
    #         G.edges[edge]['color'] = '#d36206'
    #     if 'alpha' not in G.edges[edge]:
    #         # Define un valor predeterminado para la transparencia de los bordes
    #         G.edges[edge]['alpha'] = 1
    #     if 'linewidth' not in G.edges[edge]:
    #         # Define un ancho de línea predeterminado para los bordes
    #         G.edges[edge]['linewidth'] = default_linewidth
