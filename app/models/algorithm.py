import heapq
import os
from matplotlib import pyplot as plt
from networkx import MultiDiGraph
import osmnx as ox


from data.constants import (
    IMAGES_DIR, ROAD_DIR
)


class Algorithm:
    ''' Class Algorithm is used to execute all different algorithms. '''

    def __init__(self, graph: MultiDiGraph) -> None:
        self._G: MultiDiGraph = graph

    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph

    """ Functions """

    def store_plot_graph(self, step: int, is_road: bool = False):
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
            ax=ax,
        )

        # Añadir el título con el número de iteración
        ax.set_title(f'Step {step}', color='white')
        ax.set_axis_off()

        # Determinar la carpeta destino en función de la ruta
        save_dir = IMAGES_DIR
        if is_road:
            save_dir = ROAD_DIR

        plt.savefig(
            os.path.join(save_dir, f'image_{step}.png'), facecolor='black'
        )
        plt.close(_)

    def euc_distance(self, node1, node2):
        x1, y1 = self._G.nodes[node1]['x'], self._G.nodes[node1]['y']
        x2, y2 = self._G.nodes[node2]['x'], self._G.nodes[node2]['y']
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

    def a_star(self, origen, destino):
        # print('\n\nGRAPH::', [
        #     node
        #     for node in self._G.nodes(data=True)
        # ])
        step = 0
        for node in self._G.nodes:
            self._G.nodes[node]['previous'] = None
            self._G.nodes[node]['size'] = 0
            self._G.nodes[node]['g_score'] = float('inf')
            self._G.nodes[node]['f_score'] = float('inf')
        for edge in self._G.edges:
            self.style_unvisited_edge(edge)
        self._G.nodes[origen]['size'] = 50
        self._G.nodes[destino]['size'] = 50
        self._G.nodes[origen]['g_score'] = 0
        self._G.nodes[origen]['f_score'] = self.euc_distance(
            origen, destino
        )
        pq = [(self._G.nodes[origen]['f_score'], origen)]
        while pq:
            _, node = heapq.heappop(pq)
            if node == destino:
                print('Iteraciones:', step)
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