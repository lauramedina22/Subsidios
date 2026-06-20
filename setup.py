from datetime import datetime
from models import Proveedor, Sede, Estudiante, Consumo, crear_colecciones
from connection import obtener_bd
from services import ProveedorService, SedeService, EstudianteService, ConsumoService

db = obtener_bd()
crear_colecciones(db)

proveedor_svc = ProveedorService()
sede_svc = SedeService()
estudiante_svc = EstudianteService()
consumo_svc = ConsumoService()

proveedor1 = Proveedor(
    nombre_empresa="Distribuidora ABC",
    nit="900123456-7",
    contacto_nombre="Carlos Pérez",
    telefono="3001234567",
    correo="contacto@abc.com",
    frecuencia_entrega="Semanal",
    estado_activo=True
)
proveedor_svc.insertar(proveedor1)
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
sede_svc.insertar(sede1)
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
estudiante_svc.insertar(estudiante1)
print("Estudiante insertado:", estudiante1._id)

consumo1 = Consumo(
    estudiante_id=estudiante1._id,
    sede_id=sede1._id,
    fecha_consumo=datetime(2026, 6, 20),
    hora_ingreso="12:30",
    validacion_identidad=True
)
consumo_svc.insertar(consumo1)
print("Consumo insertado:", consumo1._id)

print("\n--- Resumen de documentos ---")
print("Proveedores:", len(proveedor_svc.obtener_todos()))
print("Sedes:", len(sede_svc.obtener_todos()))
print("Estudiantes:", len(estudiante_svc.obtener_todos()))
print("Consumos:", len(consumo_svc.obtener_todos()))
