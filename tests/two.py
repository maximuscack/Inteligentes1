import networkx as nx
import matplotlib.pyplot as plt
import json

# Leer el JSON
with open('app/data/ficheros/cero.json', 'r') as file:
    data = json.load(file)

# Crear un grafo vacío
G = nx.DiGraph()

# Agregar nodos al grafo con sus posiciones predefinidas
for nodo_data in data['grafo']['nodos']:
    id_nodo = nodo_data['id']
    posicion = tuple(nodo_data['posicion'])
    G.add_node(id_nodo, pos=posicion)

# Agregar arcos al grafo
for arco_data in data['grafo']['arcos']:
    G.add_edge(
        arco_data['origen'], arco_data['destino'], id=arco_data['id']
    )

# Dibujar el grafo con las posiciones predefinidas
posiciones_predefinidas = nx.get_node_attributes(G, 'pos')
plt.figure(figsize=(8, 6))
nx.draw(
    G, pos=posiciones_predefinidas, with_labels=True, node_size=3000,
    node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray', arrowsize=20
)

plt.title('Grafo con Posiciones Predefinidas')
plt.axis('off')
plt.show()
