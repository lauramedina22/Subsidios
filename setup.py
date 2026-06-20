from datetime import datetime
from connection import obtener_bd
from models import Proveedor, Sede, Estudiante, Consumo, crear_colecciones

db = obtener_bd()
crear_colecciones(db)

proveedor1 = Proveedor(
    nombre_empresa="Distribuidora ABC",
    nit="900123456-7",
    contacto_nombre="Carlos Pérez",
    telefono="3001234567",
    correo="contacto@abc.com",
    productos_suministrados=["arroz", "pollo", "verduras"],
    frecuencia_entrega="Semanal",
    estado_activo=True
)
db.proveedores.insert_one(proveedor1.to_dict())
print("Proveedor insertado:", proveedor1._id)

sede1 = Sede(
    nombre_sede="Cafetería Central",
    ubicacion="Bloque 5",
    capacidad_maxima=200,
    cupos_disponibles=180,
    horario_atencion="11:00 - 14:00",
    estado_activo=True,
    proveedor_id=proveedor1._id
)
db.sedes.insert_one(sede1.to_dict())
print("Sede insertada:", sede1._id)

estudiante1 = Estudiante(
    codigo_estudiante="2021145632",
    nombre_completo="María Gómez",
    correo="maria.gomez@uni.edu",
    telefono="3109876543",
    facultad="Ingeniería",
    programa="Ingeniería de Sistemas",
    semestre=6,
    estrato=2,
    fecha_inicio_subsidio=datetime(2026, 1, 20),
    fecha_fin_subsidio=datetime(2026, 6, 15),
    tipo_almuerzo="Normal",
    subsidio_activo=True
)
db.estudiantes.insert_one(estudiante1.to_dict())
print("Estudiante insertado:", estudiante1._id)

consumo1 = Consumo(
    estudiante_id=estudiante1._id,
    sede_id=sede1._id,
    fecha_consumo=datetime(2026, 6, 20),
    hora_ingreso="12:30",
    validacion_identidad=True
)
db.consumos.insert_one(consumo1.to_dict())
print("Consumo insertado:", consumo1._id)

print("\n--- Resumen de documentos ---")
print("Proveedores:", db.proveedores.count_documents({}))
print("Sedes:", db.sedes.count_documents({}))
print("Estudiantes:", db.estudiantes.count_documents({}))
print("Consumos:", db.consumos.count_documents({}))
