from bson import ObjectId


class Sede:
    def __init__(self, nombre_sede, ubicacion, capacidad_maxima, estado_activo,
                 proveedor_id, cupos_disponibles=None, horario_atencion=None, _id=None):
        self._id = _id or ObjectId()
        self.nombre_sede = nombre_sede
        self.ubicacion = ubicacion
        self.capacidad_maxima = capacidad_maxima
        self.cupos_disponibles = cupos_disponibles or capacidad_maxima
        self.horario_atencion = horario_atencion
        self.estado_activo = estado_activo
        self.proveedor_id = proveedor_id

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
