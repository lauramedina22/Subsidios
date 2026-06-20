from bson import ObjectId


class Estudiante:
    coleccion = "estudiantes"

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["codigo_estudiante", "nombre_completo", "correo", "subsidio_activo"],
            "properties": {
                "codigo_estudiante": {"bsonType": "string"},
                "nombre_completo": {"bsonType": "string"},
                "correo": {"bsonType": "string"},
                "telefono": {"bsonType": "string"},
                "facultad": {"bsonType": "string"},
                "programa": {"bsonType": "string"},
                "semestre": {"bsonType": "int"},
                "estrato": {"bsonType": "int"},
                "fecha_inicio_subsidio": {"bsonType": "date"},
                "fecha_fin_subsidio": {"bsonType": "date"},
                "tipo_almuerzo": {"bsonType": "string"},
                "subsidio_activo": {"bsonType": "bool"}
            }
        }
    }

    def __init__(self, codigo_estudiante, nombre_completo, correo, subsidio_activo,
                 telefono=None, facultad=None, programa=None, semestre=None,
                 estrato=None, fecha_inicio_subsidio=None, fecha_fin_subsidio=None,
                 tipo_almuerzo=None, _id=None):
        self._id = _id or ObjectId()
        self.codigo_estudiante = codigo_estudiante
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.telefono = telefono
        self.facultad = facultad
        self.programa = programa
        self.semestre = semestre
        self.estrato = estrato
        self.fecha_inicio_subsidio = fecha_inicio_subsidio
        self.fecha_fin_subsidio = fecha_fin_subsidio
        self.tipo_almuerzo = tipo_almuerzo
        self.subsidio_activo = subsidio_activo

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
