import heapq
import os
import random
from matplotlib import pyplot as plt
from networkx import MultiDiGraph
import networkx as nx
import osmnx as ox


from data.constants import (
    BLACK_NODE, BLUE_NODE, GREEN_NODE, IMAGES_DIR, RED_NODE, ROAD_DIR, WHITE_NODE
)


class Algorithm:
    ''' Class Algorithm is used to execute all different algorithms. '''

    def __init__(self, graph: MultiDiGraph) -> None:
        self._G: MultiDiGraph = graph

    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph

    """ Functions """

    def store_plot_graph(self, step: int, is_road: bool = False):

        # for node in self._G.nodes:
        #     if self._G.nodes[node]['color'] == RED_NODE or self._G.nodes[node]['color'] == GREEN_NODE:
        #         print(self._G.nodes[node])

        _, ax = plt.subplots(figsize=(10, 10))

        ox.plot_graph(
            self._G,
            node_size=[self._G.nodes[node]['size']
                       for node in self._G.nodes],
            edge_color=[self._G.edges[edge]['color']
                        for edge in self._G.edges],
            edge_alpha=[self._G.edges[edge]['alpha']
                        for edge in self._G.edges],
            edge_linewidth=[self._G.edges[edge]['linewidth']
                            for edge in self._G.edges],
            node_color=[self._G.nodes[node]['color']
                        for node in self._G.nodes],
            bgcolor="#18080e",
            ax=ax,
        )

        # Añadir el título con el número de iteración
        ax.set_title(f'Step {step}', color='white')
        ax.set_axis_off()

        # Agregar etiquetas a los nodos
        for node, data in self._G.nodes(data=True):
            if 'tiempo' in data:
                ax.annotate(self._G.nodes[node]['tiempo'],
                            (data['x'], data['y']), color='white')
            else:
                ax.annotate(None, (data['x'], data['y']), color='white')

        # Determinar la carpeta destino en función de la ruta
        save_dir = IMAGES_DIR
        if is_road:
            save_dir = ROAD_DIR

        plt.savefig(
            os.path.join(save_dir, f'image_{step}.png'), facecolor='black'
        )
        plt.close(_)

    def style_unvisited_edge(self, edge):
        self._G.edges[edge]['color'] = '#d36206'
        self._G.edges[edge]['alpha'] = 0.2
        self._G.edges[edge]['linewidth'] = 0.5

    def style_visited_edge(self, edge):
        self._G.edges[edge]["color"] = "#d36206"
        self._G.edges[edge]["alpha"] = 1
        self._G.edges[edge]["linewidth"] = 1

    def style_active_edge(self, edge):
        self._G.edges[edge]['color'] = '#e8a900'
        self._G.edges[edge]['alpha'] = 1
        self._G.edges[edge]['linewidth'] = 1

    def style_path_edge(self, edge):
        self._G.edges[edge]['color'] = 'white'
        self._G.edges[edge]['alpha'] = 1
        self._G.edges[edge]['linewidth'] = 1

    def euc_distance(self, node1, node2):
        x1, y1 = self._G.nodes[node1]['x'], self._G.nodes[node1]['y']
        x2, y2 = self._G.nodes[node2]['x'], self._G.nodes[node2]['y']
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

    def reconstruct_path(self, origen, destino, algorithm=None):
        path_edges = []
        for edge in self._G.edges:
            self.style_unvisited_edge(edge)
        dist = 0
        speeds = []
        curr = destino
        step = 0
        while curr != origen:
            prev = self._G.nodes[curr]['previous']
            dist += self._G.edges[(prev, curr, 0)]['length']
            speeds.append(self._G.edges[(prev, curr, 0)]['maxspeed'])
            edge = (prev, curr, 0)
            if edge in self._G.edges:
                self.style_path_edge(edge)
                path_edges.append(edge)  # Agregar la arista al camino
                if algorithm:
                    self._G.edges[edge][f'{algorithm}_uses'] \
                        = self._G.edges[edge].get(f'{algorithm}_uses', 0) + 1
            else:
                print(f"Error: Edge {edge} not found in graph")
            curr = prev
            self.store_plot_graph(step, is_road=True)
            step += 1
        dist /= 1000
        print(f'Distance: {dist}')
        print(f'Avg. speed: {sum(speeds)/len(speeds)}')
        print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')

    """ Primer punto """

    def a_star_shortest_path(self, origen, destino):
        step = 0
        for node in self._G.nodes:
            self._G.nodes[node]['previous'] = None
            self._G.nodes[node]['size'] = 0
            self._G.nodes[node]['g_score'] = float('inf')
            self._G.nodes[node]['f_score'] = float('inf')
        for edge in self._G.edges:
            self.style_unvisited_edge(edge)
        self._G.nodes[origen]['f_score'] = self.euc_distance(
            origen, destino
        )
        self._G.nodes[origen]['color'] = '#ffffff'
        self._G.nodes[origen]['size'] = 50
        self._G.nodes[origen]['g_score'] = 0

        self._G.nodes[destino]['color'] = '#ffffff'
        self._G.nodes[destino]['size'] = 50
        pq = [(self._G.nodes[origen]['f_score'], origen)]
        while pq:
            _, node = heapq.heappop(pq)
            if node == destino:
                print('Iters:', step)

                self.store_plot_graph(step)
                return
            for edge in self._G.out_edges(node):
                self.style_visited_edge((edge[0], edge[1], 0))
                neighbor = edge[1]
                tentative_g_score = self._G.nodes[node]['g_score'] + \
                    self.euc_distance(node, neighbor)
                if tentative_g_score < self._G.nodes[neighbor]['g_score']:
                    self._G.nodes[neighbor]['previous'] = node
                    self._G.nodes[neighbor]['g_score'] = tentative_g_score
                    self._G.nodes[neighbor]['f_score'] = tentative_g_score + \
                        self.euc_distance(neighbor, destino)
                    heapq.heappush(
                        pq, (self._G.nodes[neighbor]
                             ['f_score'], neighbor)
                    )
                    for edge2 in self._G.out_edges(neighbor):
                        self.style_active_edge(
                            (edge2[0], edge2[1], 0)
                        )
            self.store_plot_graph(step)
            step += 1

    """ Segundo punto """

    def a_star_traffic_lights(self, origen: int, destino: int):

        for node in self._G.nodes:
            self._G.nodes[node]['previous'] = None
            self._G.nodes[node]['g_score'] = float('inf')
            self._G.nodes[node]['f_score'] = float('inf')

            if random.random() < 0.15:
                self._G.nodes[node]['tiempo'] = random.randint(1, 10)
                self._G.nodes[node]['color'] = RED_NODE

                if random.random() < 0.5:
                    self._G.nodes[node]['color'] = GREEN_NODE

            if random.random() < 0.0125:
                self._G.nodes[node]['es_turistico'] = True
                self._G.nodes[node]['color'] = BLUE_NODE

        for edge in self._G.edges:
            self.style_unvisited_edge(edge)
        self._G.nodes[origen]['f_score'] = self.euc_distance(origen, destino)
        self._G.nodes[origen]['color'] = WHITE_NODE
        self._G.nodes[origen]['size'] = 50
        self._G.nodes[origen]['g_score'] = 0
        self._G.nodes[destino]['color'] = WHITE_NODE
        self._G.nodes[destino]['size'] = 50

        # print('LLAVES1::', set([
        #     self._G.nodes[node]['color'] for node in self._G.nodes
        # ]))

        pq = [(self._G.nodes[origen]['f_score'], origen)]
        step = 0
        self.store_plot_graph(step)

        while pq:
            for node in self._G.nodes:
                if 'tiempo' in self._G.nodes[node]:
                    self._G.nodes[node]['tiempo'] -= 1
                    if self._G.nodes[node]['tiempo'] == 0:
                        self._G.nodes[node]['tiempo'] = 10

                        if self._G.nodes[node]['color'] == RED_NODE:
                            self._G.nodes[node]['color'] = GREEN_NODE
                        else:
                            self._G.nodes[node]['color'] = RED_NODE

            _, node = heapq.heappop(pq)
            if node == destino:
                # if plot:
                print('Iteraciones:', step)
                self.store_plot_graph(step)
                return
            for edge in self._G.out_edges(node):
                self.style_visited_edge((edge[0], edge[1], 0))
                neighbor = edge[1]

                # Check if the traffic light is green
                if 'traffic_light_wait' in self._G.edges[(node, neighbor, 0)]:
                    if self._G.nodes[neighbor]['color'] == RED_NODE:
                        continue  # Skip this neighbor if the traffic light is red

                tentative_g_score = self._G.nodes[node]['g_score'] + \
                    self.euc_distance(node, neighbor)
                # considera el tiempo de viaje en función de la distancia y la velocidad máxima
                travel_time = self._G.edges[(node, neighbor, 0)]['weight']
                # Añade el tiempo de espera en semáforos al tiempo de viaje
                travel_time +=\
                    self._G.edges[(node, neighbor, 0)]\
                    .get('traffic_light_wait', 0)
                tentative_g_score +=\
                    self._G.edges[(node, neighbor, 0)]\
                    .get('traffic_light_wait', 0)

                if tentative_g_score < self._G.nodes[neighbor]['g_score']:
                    self._G.nodes[neighbor]['previous'] = node
                    self._G.nodes[neighbor]['g_score'] = tentative_g_score
                    self._G.nodes[neighbor]['f_score'] =\
                        tentative_g_score + \
                        self.euc_distance(neighbor, destino)
                    heapq.heappush(
                        pq, (self._G.nodes[neighbor]['f_score'], neighbor)
                    )
                    for edge2 in self._G.out_edges(neighbor):
                        self.style_active_edge((edge2[0], edge2[1], 0))
            self.store_plot_graph(step)
            step += 1
        print(travel_time)

    """ Tercer punto """

    def dijkstra_less_fuel_path(
            self, origen: int, destino: int, fuel_efficiency: float
    ):
        visited = set()  # Conjunto de nodos visitados
        total_fuel_consumed = 0  # Total de combustible consumido
        for node in self._G.nodes:
            self._G.nodes[node]['previous'] = None
            self._G.nodes[node]['size'] = 0
            self._G.nodes[node]['g_score'] = float('inf')
        for edge in self._G.edges(keys=True):
            self.style_unvisited_edge(edge)
        self._G.nodes[origen]['color'] = '#ffffff'
        self._G.nodes[origen]['size'] = 50
        self._G.nodes[origen]['g_score'] = 0

        self._G.nodes[destino]['color'] = '#ffffff'
        self._G.nodes[destino]['size'] = 50

        pq = [(0, origen)]
        step = 0
        while pq:
            _, node = heapq.heappop(pq)
            if node == destino:
                print('Iteraciones:', step)
                self.store_plot_graph(step)
                return
            if node in visited:
                continue
            visited.add(node)
            for edge in self._G.out_edges(node, keys=True):
                self.style_visited_edge((edge[0], edge[1], edge[2]))
                neighbor = edge[1]
                edge_length = self._G.edges[edge]['length']
                max_speed = self._G.edges[edge]['maxspeed']
                fuel_consumption = (
                    edge_length / (max_speed * fuel_efficiency)
                )
                total_fuel_consumed += fuel_consumption
                tentative_g_score = self._G.nodes[node]['g_score'] + \
                    fuel_consumption
                if tentative_g_score < self._G.nodes[neighbor]['g_score']:
                    self._G.nodes[neighbor]['previous'] = node
                    self._G.nodes[neighbor]['g_score'] = tentative_g_score
                    heapq.heappush(
                        pq, (self._G.nodes[neighbor]['g_score'], neighbor))
                    for edge2 in self._G.out_edges(neighbor, keys=True):
                        self.style_active_edge((edge2[0], edge2[1], edge2[2]))
                    fuel_used = fuel_consumption * fuel_efficiency
                    print(
                        f'Used {fuel_used: .2f} gallons of fuel for edge {edge}'
                    )

                self.store_plot_graph(step)
                step += 1

            print(f'total = {total_fuel_consumed:.2f} gallons')
