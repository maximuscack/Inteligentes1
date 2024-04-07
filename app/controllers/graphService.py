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
            prefer_canvas=True,
        )
        for nodo, data in graph.nodes(data=True):
            folium.Marker(
                location=(data['y'], data['x']),
                popup=str(nodo),
                # icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)
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
            self._G.nodes[node]['color'] = '#000000'

            # if random.random() < 0.15:
            #     self._G.nodes[node]['tiempo'] = 10

            #     self._G.nodes[node]['semaforo_rojo'] = True
            #     self._G.nodes[node]['color'] = '#ffcccc'

            #     if random.random() < 0.5:
            #         self._G.nodes[node]['semaforo_rojo'] = False
            #         self._G.nodes[node]['color'] = '#ccffcc'

            # if random.random() < 0.0125:
            #     self._G.nodes[node]['es_turistico'] = True
            #     self._G.nodes[node]['color'] = '#ccccff'
