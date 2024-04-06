import os
import imageio
from streamlit_folium import folium_static
import osmnx as ox
import streamlit as st
from networkx import MultiDiGraph

from models.algorithm import Algorithm
from controllers.graphService import GraphService
from data.constants import (
    NOMBRES_BARRIOS, IMAGES_DIR, CIUDAD_MANIZALES_DIR
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

        # print('\n\n',[
        #     node
        #     for node in self._G.nodes(data=True)
        # ])

        st.title('Encuentra tu ruta')
        col1, col2 = st.columns(2)

        with col1:
            origen = st.text_input('Origen', '')
        with col2:
            destino = st.text_input('Destino', '')

        if (origen != '' and destino != '') and st.button('Hallar ruta'):
            self.limpiar_carpeta()

            origen = int(origen)
            destino = int(destino)

            self.aService.a_star(
                origen, destino
            )
            # reconstruct_path(graph, origen, destino, plot=True)

            image_files = [
                f'{IMAGES_DIR}/image_{i}.png'
                for i in range(len(os.listdir(IMAGES_DIR)))
            ]

            images = []
            for filename in image_files:
                if os.path.exists(filename):
                    images.append(imageio.imread(filename))
                else:
                    print(f"Error: No se pudo encontrar el archivo {filename}")

            print('images:', images)

            if images:
                animation_path = f'{IMAGES_DIR}/animation.gif'
                imageio.mimsave(
                    animation_path,
                    images, fps=3
                )
                self.render_animation(image_files)

            else:
                print("Error: No hay imágenes para crear la animación")

    def render_animation(self, image_files):
        animation = st.empty()
        while True:
            for filename in image_files:
                if os.path.exists(filename):
                    image = imageio.imread(filename)
                    animation.image(
                        image, caption='Animation',
                        use_column_width=True
                    )
                else:
                    print(f"Error: No se pudo encontrar el archivo {filename}")

    def graficar_mapa(self, mapa):
        st.write('Mapa:')
        folium_static(mapa)

    def limpiar_carpeta(self):
        files = os.listdir(IMAGES_DIR)
        for file in files:
            os.remove(os.path.join(IMAGES_DIR, file))
