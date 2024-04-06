from enum import Enum

#Esta es una clase enum que se utiliza para organizar y acceder fácilmente a 
# las propiedades de los nodos.
class NodeProps(Enum):
    ''' Class NodeProps is used to access easily nodes properties. '''
    NODE_ID: int = 0
    NODE_DATA: int = 1
