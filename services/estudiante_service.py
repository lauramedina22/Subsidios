from bson import ObjectId
from connection import obtener_bd
from models import Estudiante


class EstudianteService:
    def __init__(self):
        self.db = obtener_bd()
        self.coleccion = self.db.estudiantes

    def insertar(self, estudiante):
        self.coleccion.insert_one(estudiante.to_dict())

    def obtener_todos(self):
        return [Estudiante.from_dict(doc) for doc in self.coleccion.find()]

    def obtener_pagina(self, pagina: int = 1, por_pagina: int = 30):
        skip = (pagina - 1) * por_pagina
        docs = self.coleccion.find().skip(skip).limit(por_pagina)
        return [Estudiante.from_dict(doc) for doc in docs]

    def contar(self) -> int:
        return self.coleccion.count_documents({})

    def buscar_con_filtro(self, filtro, pagina=1, por_pagina=20):
        skip = (pagina - 1) * por_pagina
        pipeline = [
            {"$match": filtro},
            {"$group": {"_id": "$codigo_estudiante", "doc": {"$first": "$$ROOT"}}},
            {"$replaceWith": "$doc"},
            {"$sort": {"codigo_estudiante": 1}},
            {"$skip": skip},
            {"$limit": por_pagina}
        ]
        docs = self.coleccion.aggregate(pipeline, allowDiskUse=True)
        return [Estudiante.from_dict(doc) for doc in docs]

    def contar_con_filtro(self, filtro):
        pipeline = [
            {"$match": filtro},
            {"$group": {"_id": "$codigo_estudiante"}},
            {"$count": "total"}
        ]
        result = list(self.coleccion.aggregate(pipeline, allowDiskUse=True))
        return result[0]["total"] if result else 0

    def obtener_por_id(self, id):
        doc = self.coleccion.find_one({"_id": ObjectId(id)})
        return Estudiante.from_dict(doc) if doc else None

    def actualizar(self, id, datos):
        self.coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

    def eliminar(self, id):
        self.coleccion.delete_one({"_id": ObjectId(id)})