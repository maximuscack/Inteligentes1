from networkx import MultiDiGraph


class GraphService:
    ''' Class GraphService is used to act over the graph. '''

    def __init__(self, graph: MultiDiGraph) -> None:
        self._graph: MultiDiGraph = graph
