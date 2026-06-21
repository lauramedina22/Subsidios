from bson import ObjectId
from connection import obtener_bd
from models import Consumo


class ConsumoService:
    def __init__(self):
        self.db = obtener_bd()
        self.coleccion = self.db.consumos

    def insertar(self, consumo):
        self.coleccion.insert_one(consumo.to_dict())

    def obtener_todos(self):
        return [Consumo.from_dict(doc) for doc in self.coleccion.find()]

    def obtener_pagina(self, pagina: int = 1, por_pagina: int = 30):
        skip = (pagina - 1) * por_pagina
        docs = self.coleccion.find().skip(skip).limit(por_pagina)
        return [Consumo.from_dict(doc) for doc in docs]

    def contar(self) -> int:
        return self.coleccion.count_documents({})

    def obtener_por_id(self, id):
        doc = self.coleccion.find_one({"_id": ObjectId(id)})
        return Consumo.from_dict(doc) if doc else None

    def actualizar(self, id, datos):
        self.coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

    def eliminar(self, id):
        self.coleccion.delete_one({"_id": ObjectId(id)})