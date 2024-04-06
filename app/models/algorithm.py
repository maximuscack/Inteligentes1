import heapq
import os
from networkx import MultiDiGraph
import osmnx as ox


from data.constants import (
    IMAGES_DIR
)


class Algorithm:
    ''' Class Algorithm is used to execute all different algorithms. '''

    def __init__(self, graph: MultiDiGraph) -> None:
        self._G: MultiDiGraph = graph

    def set_graph(self, graph: MultiDiGraph) -> None:
        self._G = graph

    """ Functions """

    def store_plot_graph(self, step):
        # No es necesario crear la figura y el subplot aquí
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
            save=True,
            filepath=os.path.join(IMAGES_DIR, f'image_{step}.png'),
            show=False, close=True
        )

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
            # print('\n', node, '\n')
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
        # Si deseas guardar una imagen al final de la búsqueda
        # self.store_plot_graph(step)

    # def reconstruct_path(self, origen, destino, plot=False, algorithm=None):
    #     for edge in graph.edges:
    #         style_unvisited_edge(graph, edge)
    #     dist = 0
    #     speeds = []
    #     curr = destino
    #     step = 0
    #     while curr != origen:
    #         prev = graph.nodes[curr]['previous']
    #         dist += graph.edges[(prev, curr, 0)]['length']
    #         speeds.append(graph.edges[(prev, curr, 0)]['maxspeed'])
    #         edge = (prev, curr, 0)
    #         if edge in graph.edges:  # Ensure the edge exists in the graph
    #             style_path_edge(graph, edge, step)
    #             if algorithm:
    #                 graph.edges[edge][f'{algorithm}_uses'] \
    #                     = graph.edges[edge].get(f'{algorithm}_uses', 0) + 1
    #         else:
    #             print(f"Error: Edge {edge} not found in graph")
    #         curr = prev
    #         step += 1
    #     dist /= 1000
    #     if plot:
    #         print(f'Distance: {dist}')
    #         print(f'Avg. speed: {sum(speeds)/len(speeds)}')
    #         print(f'Total time: {dist/(sum(speeds)/len(speeds)) * 60}')
    #         plot_graph(graph, step)

    def style_unvisited_edge(self, edge):
        self._G.edges[edge]['color'] = '#d36206'
        self._G.edges[edge]['alpha'] = 0.2
        self._G.edges[edge]['linewidth'] = 0.5
        # plot_graph(graph)

    def style_visited_edge(self, edge):
        self._G.edges[edge]["color"] = "#d36206"
        self._G.edges[edge]["alpha"] = 1
        self._G.edges[edge]["linewidth"] = 1

    def style_active_edge(self, edge):
        self._G.edges[edge]['color'] = '#e8a900'
        self._G.edges[edge]['alpha'] = 1
        self._G.edges[edge]['linewidth'] = 1
        # plot_graph(graph, step)

    def style_path_edge(self, edge):
        self._G.edges[edge]['color'] = 'white'
        self._G.edges[edge]['alpha'] = 1
        self._G.edges[edge]['linewidth'] = 1
        # plot_graph(graph, step)
