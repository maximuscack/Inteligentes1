class Arco:
    ''' Class Arista is used to . '''

    def __init__(
        self, id: str, origen: str, destino: str,
        es_calle: bool, es_creciente: bool, distancia: int
    ) -> None:
        self._id: str = id
        self._origen: str = origen
        self._destino: str = destino
        self._es_calle: bool = es_calle
        self._es_creciente: bool = es_creciente
        self._distancia: int = distancia

    def set_origen(self, origen: str) -> None:
        ''' Method that sets the origin of the edge. '''
        self._origen = origen

    def set_destino(self, destino: str) -> None:
        ''' Method that sets the destination of the edge. '''
        self._destino = destino

    def get_id(self) -> str:
        ''' Method that returns the id of the edge. '''
        return self._id

    def get_origen(self) -> str:
        ''' Method that returns the origin of the edge. '''
        return self._origen

    def get_destino(self) -> str:
        ''' Method that returns the destination of the edge. '''
        return self._destino

    def get_es_calle(self) -> bool:
        ''' Method that returns if the edge is a street. '''
        return self._es_calle

    def get_es_creciente(self) -> bool:
        ''' Method that returns if the edge is increasing. '''
        return self._es_creciente

    def get_distancia(self) -> int:
        ''' Method that returns the distance of the edge. '''
        return self._distancia
