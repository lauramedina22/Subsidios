from bson import ObjectId


class Menu:
    coleccion = "Menus_Diarios"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sede_id", "fecha", "tipo_comida", "plato"],
            "properties": {
                "sede_id":    {"bsonType": "objectId"},
                "fecha":      {"bsonType": "string"},
                "tipo_comida": {
                    "bsonType": "string",
                    "enum": ["carnivoro", "vegetariano"]
                },
                "plato":      {"bsonType": "string"},
                "info_nutricional": {
                    "bsonType": "object",
                    "properties": {
                        "calorias":      {"bsonType": "string"},
                        "proteinas":     {"bsonType": "string"},
                        "carbohidratos": {"bsonType": "string"},
                        "grasas":        {"bsonType": "string"}
                    }
                },
                "ingredientes":          {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "advertencia_alergias": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
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
        data.pop("_id", None)
        return cls(**data)