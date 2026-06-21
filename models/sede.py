from bson import ObjectId


class Sede:
    coleccion = "sedes"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre_sede", "ubicacion", "capacidad_maxima", "estado_activo"],
            "properties": {
                "nombre_sede":      {"bsonType": "string"},
                "ubicacion":        {"bsonType": "string"},
                "capacidad_maxima": {"bsonType": "int"},
                "horario_atencion": {
                    "bsonType": "object",
                    "properties": {
                        "apertura": {"bsonType": "string"},
                        "cierre":   {"bsonType": "string"}
                    }
                },
                "estado_activo": {"bsonType": "bool"}
            }
        }
    }

    def __init__(self, nombre_sede, ubicacion, capacidad_maxima, estado_activo,
                 horario_atencion=None, _id=None):
        self._id             = _id or ObjectId()
        self.nombre_sede     = nombre_sede
        self.ubicacion       = ubicacion
        self.capacidad_maxima = capacidad_maxima
        self.horario_atencion = horario_atencion or {"apertura": "11:00", "cierre": "15:00"}
        self.estado_activo   = estado_activo

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data.pop("_id", None)
        return cls(**data)