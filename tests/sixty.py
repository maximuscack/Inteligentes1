# import os
# import streamlit as st
# import osmnx as ox
# import folium
# import googlemaps as gmaps
# from streamlit_folium import folium_static

# # Clave de la API de Google Maps
# google_maps_api_key = "AIzaSyBDaeWicvigtP9xPv919E-RNoxfvC-Hqik&callback"

# CIUDAD_MANIZALES_DIR = 'app/data/mapas/'

# barrios = [
#     'Comuna Palogrande', 'Comuna La Fuente',
#     'Comuna San José', 'Comuna Nuevo Horizonte',
#     'Comuna Atardeceres', 'Comuna Ciudadela del Norte',
#     'Comuna Ecoturística Cerro de Oro', 'Comuna Universitaria',
#     'Comuna Cumanday', 'Comuna La Macarena',
# ]

# # Lista para almacenar los gráficos de los barrios
# graficos = []

# # Cargar los mapas de los barrios y guardarlos en la lista
# for barrio in barrios:
#     filepath = os.path.join(CIUDAD_MANIZALES_DIR, f'{barrio}.graphml')
#     if os.path.exists(filepath):
#         graph = ox.load_graphml(filepath)
#     else:
#         place_name = f'{barrio}, Caldas, Colombia'
#         graph = ox.graph_from_place(place_name, network_type='all')
#         ox.save_graphml(graph, filepath=filepath)
#     graficos.append(graph)

# # Configurar la interfaz de usuario con Streamlit
# st.title('Selecciona un barrio para mostrar su gráfico:')
# barrio_seleccionado = st.selectbox('Barrios', barrios)

# # Obtener el índice del barrio seleccionado
# indice_barrio = barrios.index(barrio_seleccionado)

# # Obtener el gráfico del barrio seleccionado
# graph = graficos[indice_barrio]

# # Crear un cliente de Google Maps
# gmaps = gmaps.Client(key=google_maps_api_key)

# # Crear un mapa interactivo con Folium centrado en el barrio seleccionado
# for node in graph.nodes:
#     node_data = graph.nodes[node]
#     if 'y' in node_data and 'x' in node_data:
#         lat, lon = node_data['y'], node_data['x']
#         location_info = gmaps.reverse_geocode((lat, lon))
#         address = location_info[0]['formatted_address']
#         break

# mapa = folium.Map(location=[lat, lon], zoom_start=15,
#                   control_scale=True, zoom_control=False)

# # Añadir los nodos del gráfico al mapa
# for nodo, data in graph.nodes(data=True):
#     folium.Marker(location=(data['y'], data['x']),
#                   popup=f"{nodo}: {address}").add_to(mapa)

# # Mostrar el mapa interactivo
# st.write(f'Mapa de {barrio_seleccionado}:')
# folium_static(mapa)
