from .proveedor import Proveedor
from .sede import Sede
from .estudiante import Estudiante
from .consumo import Consumo

MODELOS = [Proveedor, Sede, Estudiante, Consumo]


def crear_colecciones(db):
    for modelo in MODELOS:
        if modelo.coleccion not in db.list_collection_names():
            db.create_collection(modelo.coleccion, validator=modelo.schema)
