import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Agregar atributo de la ciudad al grafo
ciudad = 'Manizales'
es_dirigido = True

# Crear un grafo vacío
G = nx.DiGraph()

G.graph['ciudad'] = ciudad

# Agregar nodos al grafo #
nodos = [
    {
        'id': 'FCD247',
        'barrio': 'San Jorge',
        'es_turistico': True,
        'semaforo': {
            'habilitado': True,
            'en_rojo': True,
            'tiempo_por_estado': 10
        }
    },
    {
        'id': 'ACD237',
        'lugar': 'Solferino',
        'barrio': 'Trinidad',
        'es_turistico': True,
        'semaforo': {
            'habilitado': False,
            'en_rojo': False,
            'tiempo_por_estado': 10
        }
    }
]
# Agregar arcos al grafo
arcos = [
    {
        'id': 'SAB234',
        'origen': 'ACD237',
        'destino': 'FCD247',
        'es_calle': True,
        'es_creciente': True,
        'distancia': 100
    }
]

for nodo in nodos:
    G.add_node(
        nodo['id'], barrio=nodo['barrio'],
        es_turistico=nodo['es_turistico'], semaforo=nodo['semaforo']
    )
for arco in arcos:
    G.add_edge(
        arco['origen'],
        arco['destino'],
        id=arco['id'], es_calle=arco['es_calle'],
        es_creciente=arco['es_creciente'], distancia=arco['distancia']
    )


# Crear una lista de colores para las aristas (rojo en el segundo 5)
edge_colors = ['black' if i != 5 else 'red' for i in range(101)]

# Crear una figura y establecer el tamaño
fig = plt.figure(figsize=(15, 10))
# Obtener la posición de los nodos
pos = nx.spring_layout(G, k=0.3, iterations=50)
# Obtener las etiquetas de los nodos con toda la información
node_labels = {n: f"{n}\n{G.nodes[n]}" for n in G.nodes()}

# Función para actualizar la gráfica en cada frame de la animación


def update(num):
    plt.clf()
    # Dibujar el grafo en el frame actual
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=3000, node_color='skyblue',
            font_size=10, font_weight='bold', edge_color=edge_colors[num], arrowsize=20)
    plt.title(f"Grafo de la ciudad de {ciudad} - Tiempo: {num}")
    plt.axis('off')


# Crear la animación
ani = animation.FuncAnimation(fig, update, frames=range(101), repeat=False)

plt.show()
