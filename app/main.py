
from models.nodo import Nodo


nodoi: Nodo = Nodo(
    '1', 'Palermo', True, {
        'habilitado': False,
        'en_rojo': False,
        'tiempo_por_estado': 10
    })

print(nodoi.get_semaforo())

nodoi.set_semaforo({
    'habilitado': True,
    'en_rojo': True,
    'tiempo_por_estado': 10
})

print(nodoi.get_semaforo())
