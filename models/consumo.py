from bson import ObjectId


class Consumo:
    coleccion = "consumos"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["estudiante_id", "sede_id", "fecha_consumo", "validacion_identidad"],
            "properties": {
                "estudiante_id": {
                    "bsonType": "object",
                    "required": ["nombre_completo", "codigo_estudiante"],
                    "properties": {
                        "nombre_completo":   {"bsonType": "string"},
                        "codigo_estudiante": {"bsonType": "string"},
                        "tipo_almuerzo":     {"bsonType": "string"}
                    }
                },
                "sede_id": {
                    "bsonType": "object",
                    "required": ["nombre_sede"],
                    "properties": {
                        "nombre_sede": {"bsonType": "string"},
                        "ubicacion":   {"bsonType": "string"}
                    }
                },
                "menu_id": {
                    "bsonType": "object",
                    "properties": {
                        "plato":       {"bsonType": "string"},
                        "tipo_comida": {"bsonType": "string"}
                    }
                },
                "fecha_consumo": {"bsonType": "date"},
                "hora_ingreso": {"bsonType": "string"},
                "validacion_identidad": {"bsonType": "bool"}
            }
        }
    }

    def __init__(self, estudiante_id, sede_id, fecha_consumo, validacion_identidad,
                 menu_id=None, hora_ingreso=None, _id=None):
        self._id                  = _id or ObjectId()
        self.estudiante_id        = estudiante_id   # dict embebido: {nombre_completo, codigo_estudiante, tipo_almuerzo}
        self.sede_id              = sede_id         # dict embebido: {nombre_sede, ubicacion}
        self.menu_id              = menu_id         # dict embebido: {plato, tipo_comida}
        self.fecha_consumo        = fecha_consumo
        self.hora_ingreso         = hora_ingreso
        self.validacion_identidad = validacion_identidad

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data.pop("_id", None)
        return cls(**data)