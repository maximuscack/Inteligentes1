import os
import time
import imageio
from streamlit_folium import folium_static
import osmnx as ox
import streamlit as st
from networkx import MultiDiGraph


from models.algorithm import Algorithm
from controllers.graphService import GraphService
from data.constants import (
    NOMBRES_BARRIOS, IMAGES_DIR, ROAD_DIR
)


class Menu:
    ''' Class Menu is used to render to user. '''

    def __init__(self) -> None:
        self._G: MultiDiGraph = MultiDiGraph()
        self.gService: GraphService = GraphService(self._G)
        self.aService: Algorithm = Algorithm(self._G)

    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph
        self.gService.set_graph(graph)
        self.aService.set_graph(graph)

    """ Specialized methods """

    def render(self):
        # st.set_page_config(layout="wide")

        barrios: list[MultiDiGraph] = self.gService\
            .load_neighborhoods(NOMBRES_BARRIOS)

        st.title('Selecciona un barrio para mostrar su gráfico:')
        barrio_selec = st.selectbox('Barrios', NOMBRES_BARRIOS)

        mapa, graph = self.gService.load_neighbor_data(barrio_selec, barrios)
        self.set_graph(graph)

        self.gService.reset_graph()

        self.graficar_mapa(mapa)

        st.title('Encuentra tu ruta')
        col1, col2 = st.columns(2)

        with col1:
            destino = st.text_input('Destino', '')
        with col2:
            origen = st.text_input('Origen', '')

        if (origen != '' and destino != ''):
            origen, destino = int(origen), int(destino)
            if st.button('Hallar ruta más corta'):
                self.shortest_path(origen, destino)
            elif st.button('Hallar ruta más rapida'):
                self.fastest_path(origen, destino)
            elif st.button('Hallar ruta con menor consumo de combustible'):
                self.less_fuel_path(origen, destino)
            elif st.button('Hallar ruta más económica para el pasajero'):
                self.less_cost_path(origen, destino)
            elif st.button('Hacer un Tour trip'):
                self.tour_trip(origen, destino)

    def shortest_path(self, origen: int, destino: int):
        self.limpiar_carpeta()

        # Ejecutar el algoritmo A*
        self.aService.a_star(origen, destino)

        # Reconstruir el camino y guardar las imágenes del proceso
        self.aService.reconstruct_path(origen, destino)

        # Obtener las imágenes generadas durante el algoritmo
        tree_files = [
            f'{IMAGES_DIR}/image_{i}.png'
            for i in range(len(os.listdir(IMAGES_DIR)))
        ]

        # Crear el GIF del proceso del algoritmo A*
        animation_path = f'{IMAGES_DIR}/animation.gif'
        imageio.mimsave(animation_path,
                        [imageio.imread(file) for file in tree_files],
                        fps=3)
        st.title('Animación del algoritmo')
        st.image(animation_path, caption='Animación del algoritmo A*')

        # Obtener las imágenes del camino reconstruido
        route_files = [
            f'{ROAD_DIR}/image_{i}.png'
            for i in range(len(os.listdir(ROAD_DIR)) - 1)
        ]

        # Crear el GIF del camino reconstruido
        road_animation_path = f'{ROAD_DIR}/image_animation.gif'
        imageio.mimsave(road_animation_path,
                        [imageio.imread(file) for file in route_files],
                        fps=3)
        st.title('Animación del camino más corto')
        st.image(road_animation_path, caption='Animación del camino más corto')

    def fastest_path(self, origen: int, destino: int):
        pass

    def less_fuel_path(self, origen: int, destino: int):
        pass

    def less_cost_path(self, origen: int, destino: int):
        pass

    def tour_trip(self, origen: int, destino: int):
        pass

    # def render_animation(self, image_files):
    #     animation = st.empty()
    #     # while True:
    #     for filename in image_files:
    #         time.sleep(0.5)
    #         if os.path.exists(filename):
    #             image = imageio.imread(filename)
    #             animation.image(
    #                 image, caption='Animation',
    #                 use_column_width=True
    #             )
    #         else:
    #             print(f"Error: No se pudo encontrar el archivo {filename}")

    def graficar_mapa(self, mapa):
        st.write('Mapa:')
        folium_static(mapa)

    def limpiar_carpeta(self):
        files = os.listdir(IMAGES_DIR)
        for file in files:
            os.remove(os.path.join(IMAGES_DIR, file))
