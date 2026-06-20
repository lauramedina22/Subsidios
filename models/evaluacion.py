from bson import ObjectId


class Evaluacion:
    coleccion = "Evaluaciones"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["estudiante_id", "sede_id", "fecha_evaluacion", "calificacion"],
            "properties": {
                "estudiante_id": {
                    "bsonType": "object",
                    "required": ["nombre_completo", "codigo_estudiante"],
                    "properties": {
                        "nombre_completo":    {"bsonType": "string"},
                        "codigo_estudiante":  {"bsonType": "string"},
                        "semestre":           {"bsonType": "int"},
                        "fecha_inicio_subsidio": {"bsonType": "string"},
                        "fecha_fin_subsidio":    {"bsonType": "string"}
                    }
                },
                "sede_id": {
                    "bsonType": "object",
                    "required": ["nombre_sede"],
                    "properties": {
                        "nombre_sede": {"bsonType": "string"}
                    }
                },
                "fecha_evaluacion": {"bsonType": "string"},
                "calificacion": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 5
                },
                "comentario":   {"bsonType": "string"},
                "sugerencias":  {"bsonType": "string"}
            }
        }
    }

    def __init__(self, estudiante_id, sede_id, fecha_evaluacion, calificacion,
                 comentario=None, sugerencias=None, _id=None):
        self._id               = _id or ObjectId()
        self.estudiante_id     = estudiante_id     # dict embebido
        self.sede_id           = sede_id           # dict embebido
        self.fecha_evaluacion  = fecha_evaluacion
        self.calificacion      = calificacion
        self.comentario        = comentario
        self.sugerencias       = sugerencias

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data.pop("_id", None)
        return cls(**data)