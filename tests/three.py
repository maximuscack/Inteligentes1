import networkx as nx
import matplotlib.pyplot as plt

# Definir la estructura del laberinto
laberinto = {
    "nodos": [
        {"id": "A", "pos": (0, 0)},
        {"id": "B", "pos": (1, 0)},
        {"id": "C", "pos": (0, -1)},
        {"id": "D", "pos": (1, -1)}
    ],
    "arcos": [
        {"origen": "A", "destino": "B"},
        {"origen": "A", "destino": "C"},
        {"origen": "B", "destino": "D"},
        {"origen": "C", "destino": "D"},
    ]
}

# Crear un grafo vacío
G = nx.DiGraph()

# Agregar nodos al grafo
for nodo in laberinto["nodos"]:
    G.add_node(nodo["id"], pos=nodo["pos"])

# Agregar arcos al grafo
for arco in laberinto["arcos"]:
    G.add_edge(arco["origen"], arco["destino"])

# Obtener posiciones de los nodos
posiciones = nx.get_node_attributes(G, "pos")

# Dibujar el grafo
plt.figure(figsize=(8, 6))
nx.draw(G, pos=posiciones, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray', arrowsize=20)

plt.title("Laberinto")
plt.axis('off')
plt.show()