from .proveedor  import Proveedor
from .sede       import Sede
from .estudiante import Estudiante
from .consumo    import Consumo
from .menu       import Menu
from .evaluacion import Evaluacion

MODELOS = [Proveedor, Sede, Estudiante, Consumo, Menu, Evaluacion]


def crear_colecciones(db):
    for modelo in MODELOS:
        if modelo.coleccion not in db.list_collection_names():
            db.create_collection(modelo.coleccion, validator=modelo.schema)
            print(f"  Coleccion creada: {modelo.coleccion}")
        else:
            print(f"  Coleccion ya existe: {modelo.coleccion}")