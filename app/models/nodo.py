from data.constants import CAMPOS_SEMAFORO


class Nodo:
    ''' Class Nodo es usada para . '''

    def __init__(
        self, id: str, barrio: str, es_turistico: bool, semaforo: dict
    ) -> None:
        ''' Constructor de la clase Nodo. '''
        if not self.semaforo_valido(semaforo):
            raise ValueError(
                'El semaforo no tiene los campos correctos.'
            )

        self._id: str = id
        self._barrio: str = barrio
        self._es_turistico: bool = es_turistico
        self._semaforo: dict = semaforo

    def set_semaforo(self, semaforo: dict) -> None:
        ''' Metodo que setea el semaforo del nodo. '''
        if self.semaforo_valido(semaforo):
            self._semaforo = semaforo
        else:
            raise ValueError(
                'El semaforo no tiene los campos correctos.'
            )

    def get_id(self) -> str:
        ''' Metodo que retorna el id del nodo. '''
        return self._id

    def get_barrio(self) -> str:
        ''' Metodo que retorna el barrio del nodo. '''
        return self._barrio

    def get_es_turistico(self) -> bool:
        ''' Metodo que retorna si el nodo es turistico. '''
        return self._es_turistico

    def get_semaforo(self) -> dict:
        ''' Metodo que retorna el semaforo del nodo. '''
        return self._semaforo

    def semaforo_valido(self, semaforo: dict) -> None:
        ''' Metodo que valida los campos del semaforo. '''
        return list(semaforo.keys()) == CAMPOS_SEMAFORO

    def __str__(self) -> str:
        ''' Metodo que retorna el string de la clase Nodo. '''
        return f'Nodo: {self._barrio}'
