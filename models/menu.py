from bson import ObjectId


class Menu:
    coleccion = "menus"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sede_id", "fecha", "tipo_comida", "plato"],
            "properties": {
                "sede_id": {
                    "bsonType": "object",
                    "required": ["nombre_sede"],
                    "properties": {
                        "nombre_sede": {"bsonType": "string"},
                        "ubicacion":   {"bsonType": "string"}
                    }
                },
                "fecha":       {"bsonType": "date"},
                "tipo_comida": {"bsonType": "string", "enum": ["carnivoro", "vegetariano"]},
                "plato":       {"bsonType": "string"},
                "info_nutricional": {
                    "bsonType": "object",
                    "properties": {
                        "calorias":      {"bsonType": "string"},
                        "proteinas":     {"bsonType": "string"},
                        "carbohidratos": {"bsonType": "string"},
                        "grasas":        {"bsonType": "string"}
                    }
                },
                "ingredientes":         {"bsonType": "array", "items": {"bsonType": "string"}},
                "advertencia_alergias": {"bsonType": "array", "items": {"bsonType": "string"}}
            }
        }
    }

    def __init__(self, sede_id, fecha, tipo_comida, plato,
                 info_nutricional=None, ingredientes=None,
                 advertencia_alergias=None, _id=None):
        self._id                  = _id or ObjectId()
        self.sede_id              = sede_id
        self.fecha                = fecha
        self.tipo_comida          = tipo_comida
        self.plato                = plato
        self.info_nutricional     = info_nutricional or {}
        self.ingredientes         = ingredientes or []
        self.advertencia_alergias = advertencia_alergias or []

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        _id = data.pop("_id", None)
        obj = cls.__new__(cls)
        obj._id                  = _id or ObjectId()
        obj.sede_id              = data.get("sede_id", {})
        obj.fecha                = data.get("fecha")
        obj.tipo_comida          = data.get("tipo_comida", "")
        obj.plato                = data.get("plato", "")
        obj.info_nutricional     = data.get("info_nutricional", {})
        obj.ingredientes         = data.get("ingredientes", [])
        obj.advertencia_alergias = data.get("advertencia_alergias", [])
        return obj