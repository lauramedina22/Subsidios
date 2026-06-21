from bson import ObjectId
from connection import obtener_bd
from models import Evaluacion


class EvaluacionService:
    def __init__(self):
        self.db = obtener_bd()
        self.coleccion = self.db[Evaluacion.coleccion]

    def insertar(self, evaluacion):
        self.coleccion.insert_one(evaluacion.to_dict())

    def obtener_todos(self):
        return [Evaluacion.from_dict(doc) for doc in self.coleccion.find()]

    def obtener_pagina(self, pagina: int = 1, por_pagina: int = 30):
        skip = (pagina - 1) * por_pagina
        docs = self.coleccion.find().skip(skip).limit(por_pagina)
        return [Evaluacion.from_dict(doc) for doc in docs]

    def contar(self) -> int:
        return self.coleccion.count_documents({})

    def obtener_por_id(self, id):
        doc = self.coleccion.find_one({"_id": ObjectId(id)})
        return Evaluacion.from_dict(doc) if doc else None

    def obtener_por_sede(self, nombre_sede):
        return list(self.coleccion.find({"sede_id.nombre_sede": nombre_sede}))

    def obtener_por_calificacion(self, calificacion):
        return list(self.coleccion.find({"calificacion": calificacion}))

    def actualizar(self, id, datos):
        self.coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

    def eliminar(self, id):
        self.coleccion.delete_one({"_id": ObjectId(id)})