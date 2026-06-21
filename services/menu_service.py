from bson import ObjectId
from connection import obtener_bd
from models import Menu


class MenuService:
    def __init__(self):
        self.db = obtener_bd()
        self.coleccion = self.db[Menu.coleccion]

    def insertar(self, menu):
        self.coleccion.insert_one(menu.to_dict())

    def obtener_todos(self):
        return [Menu.from_dict(doc) for doc in self.coleccion.find()]

    def obtener_pagina(self, pagina: int = 1, por_pagina: int = 30):
        skip = (pagina - 1) * por_pagina
        docs = self.coleccion.find().skip(skip).limit(por_pagina)
        return [Menu.from_dict(doc) for doc in docs]

    def contar(self) -> int:
        return self.coleccion.count_documents({})

    def obtener_por_id(self, id):
        doc = self.coleccion.find_one({"_id": ObjectId(id)})
        return Menu.from_dict(doc) if doc else None

    def obtener_por_sede_y_fecha(self, sede_id, fecha):
        return list(self.coleccion.find({
            "sede_id": ObjectId(sede_id),
            "fecha": fecha
        }))

    def obtener_por_tipo(self, tipo_comida):
        return list(self.coleccion.find({"tipo_comida": tipo_comida}))

    def actualizar(self, id, datos):
        self.coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

    def eliminar(self, id):
        self.coleccion.delete_one({"_id": ObjectId(id)})