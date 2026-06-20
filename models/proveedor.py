from bson import ObjectId


class Proveedor:
    def __init__(self, nombre_empresa, nit, telefono, correo, estado_activo=True,
                 contacto_nombre=None, productos_suministrados=None,
                 frecuencia_entrega=None, _id=None):
        self._id = _id or ObjectId()
        self.nombre_empresa = nombre_empresa
        self.nit = nit
        self.contacto_nombre = contacto_nombre
        self.telefono = telefono
        self.correo = correo
        self.productos_suministrados = productos_suministrados or []
        self.frecuencia_entrega = frecuencia_entrega
        self.estado_activo = estado_activo

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
