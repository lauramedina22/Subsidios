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
                "cupos_disponibles":{"bsonType": "int"},
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
                 horario_atencion=None, cupos_disponibles=0,
                 proveedor_id=None, _id=None):
        self._id              = _id or ObjectId()
        self.nombre_sede      = nombre_sede
        self.ubicacion        = ubicacion
        self.capacidad_maxima = capacidad_maxima
        self.cupos_disponibles = cupos_disponibles
        self.horario_atencion = horario_atencion or {"apertura": "11:00", "cierre": "15:00"}
        self.estado_activo    = estado_activo
        if proveedor_id is not None:
            self.proveedor_id = proveedor_id

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        _id = data.pop("_id", None)
        obj = cls.__new__(cls)
        obj._id = _id or ObjectId()
        obj.nombre_sede       = data.get("nombre_sede", "")
        obj.ubicacion         = data.get("ubicacion", "")
        obj.capacidad_maxima  = data.get("capacidad_maxima", 0)
        obj.cupos_disponibles = data.get("cupos_disponibles", 0)
        obj.horario_atencion  = data.get("horario_atencion", {"apertura": "11:00", "cierre": "15:00"})
        obj.estado_activo     = data.get("estado_activo", True)
        obj.proveedor_id      = data.get("proveedor_id")
        return obj