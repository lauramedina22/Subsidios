from bson import ObjectId
from connection import obtener_bd
from models import Sede


class SedeService:
    def __init__(self):
        self.db = obtener_bd()
        self.coleccion = self.db.sedes

    def insertar(self, sede):
        self.coleccion.insert_one(sede.to_dict())

    def obtener_todos(self):
        return [Sede.from_dict(doc) for doc in self.coleccion.find()]

    def obtener_por_id(self, id):
        doc = self.coleccion.find_one({"_id": ObjectId(id)})
        return Sede.from_dict(doc) if doc else None

    def actualizar(self, id, datos):
        self.coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

    def eliminar(self, id):
        self.coleccion.delete_one({"_id": ObjectId(id)})
