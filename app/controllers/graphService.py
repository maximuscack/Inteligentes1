import os
import folium
import streamlit as st
import osmnx as ox
from networkx import MultiDiGraph

from data.constants import (
    NOMBRES_BARRIOS, CIUDAD_MANIZALES_DIR
)


class GraphService:
    ''' Class GraphService is used to act over the graph. '''
    
    # Constructor de la clase, inicializa el grafo
    def __init__(self, graph: MultiDiGraph | None = None) -> None:
        self._G: MultiDiGraph = graph

    # Método para establecer el grafo
    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph

    # Método para cargar los barrios
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

    # Método para cargar los datos de los barrios seleccionados
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

    # Método para reiniciar el grafo
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
            self._G.nodes[node]['previous'] = None
            self._G.nodes[node]['size'] = 0
            self._G.nodes[node]['g_score'] = float('inf')
            self._G.nodes[node]['f_score'] = float('inf')
