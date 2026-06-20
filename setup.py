from datetime import datetime
from connection import obtener_bd
from models import Proveedor, Sede, Estudiante, Consumo

db = obtener_bd()

# -------------------------------------------------------------
# 1. PROVEEDORES
# -------------------------------------------------------------
db.create_collection("proveedores", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["nombre_empresa", "nit", "telefono", "correo", "estado_activo"],
        "properties": {
            "nombre_empresa": {"bsonType": "string"},
            "nit": {"bsonType": "string"},
            "contacto_nombre": {"bsonType": "string"},
            "telefono": {"bsonType": "string"},
            "correo": {"bsonType": "string"},
            "productos_suministrados": {"bsonType": "array", "items": {"bsonType": "string"}},
            "frecuencia_entrega": {"bsonType": "string"},
            "estado_activo": {"bsonType": "bool"}
        }
    }
}) if "proveedores" not in db.list_collection_names() else None

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

# -------------------------------------------------------------
# 2. SEDES
# -------------------------------------------------------------
db.create_collection("sedes", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["nombre_sede", "ubicacion", "capacidad_maxima", "estado_activo", "proveedor_id"],
        "properties": {
            "nombre_sede": {"bsonType": "string"},
            "ubicacion": {"bsonType": "string"},
            "capacidad_maxima": {"bsonType": "int"},
            "cupos_disponibles": {"bsonType": "int"},
            "horario_atencion": {"bsonType": "string"},
            "estado_activo": {"bsonType": "bool"},
            "proveedor_id": {"bsonType": "objectId"}
        }
    }
}) if "sedes" not in db.list_collection_names() else None

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


# 3. ESTUDIANTES

db.create_collection("estudiantes", validator={
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
}) if "estudiantes" not in db.list_collection_names() else None

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


# 4. CONSUMOS

db.create_collection("consumos", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["estudiante_id", "sede_id", "fecha_consumo", "validacion_identidad"],
        "properties": {
            "estudiante_id": {"bsonType": "objectId"},
            "sede_id": {"bsonType": "objectId"},
            "menu_id": {"bsonType": "objectId"},
            "fecha_consumo": {"bsonType": "date"},
            "hora_ingreso": {"bsonType": "string"},
            "validacion_identidad": {"bsonType": "bool"}
        }
    }
}) if "consumos" not in db.list_collection_names() else None

consumo1 = Consumo(
    estudiante_id=estudiante1._id,
    sede_id=sede1._id,
    fecha_consumo=datetime(2026, 6, 20),
    hora_ingreso="12:30",
    validacion_identidad=True
)
db.consumos.insert_one(consumo1.to_dict())
print("Consumo insertado:", consumo1._id)

# -------------------------------------------------------------
print("\n--- Resumen de documentos ---")
print("Proveedores:", db.proveedores.count_documents({}))
print("Sedes:", db.sedes.count_documents({}))
print("Estudiantes:", db.estudiantes.count_documents({}))
print("Consumos:", db.consumos.count_documents({}))
