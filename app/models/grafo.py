from models.arco import Arco
from models.nodo import Nodo


class Grafo:
    ''' Class Grafo is used to . '''

    def __init__(
        self, ciudad: str, es_dirigido: str, nodos: Nodo, arcos: Arco
    ) -> None:
        self._ciudad: str = ciudad
        self._es_dirigido: str = es_dirigido
        self._nodos: Nodo = nodos
        self._arcos: Arco = arcos
