from bson import ObjectId


class Consumo:
    def __init__(self, estudiante_id, sede_id, fecha_consumo, validacion_identidad,
                 menu_id=None, hora_ingreso=None, _id=None):
        self._id = _id or ObjectId()
        self.estudiante_id = estudiante_id
        self.sede_id = sede_id
        self.menu_id = menu_id
        self.fecha_consumo = fecha_consumo
        self.hora_ingreso = hora_ingreso
        self.validacion_identidad = validacion_identidad

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
