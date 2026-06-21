"""
insertar_sedes.py
Inserta las 5 sedes reales de la Universidad de Caldas.
"""

from connection import obtener_bd
from models import Sede, crear_colecciones

# ------------------------------------------------------------------
# Datos reales de las sedes
# ------------------------------------------------------------------
SEDES = [
    {
        "nombre_sede":      "Sede Central",
        "ubicacion":        "Calle 65 N 26-10, Manizales, Caldas",
        "capacidad_maxima": 300,
        "estado_activo":    True
    },
    {
        "nombre_sede":      "Sede Palogrande",
        "ubicacion":        "Av. Santander N 5865, Manizales, Caldas",
        "capacidad_maxima": 200,
        "estado_activo":    True
    },
    {
        "nombre_sede":      "Palacio de Bellas Artes",
        "ubicacion":        "Calle 13 N 202, Chipre, Manizales, Caldas",
        "capacidad_maxima": 250,
        "estado_activo":    True
    },
    {
        "nombre_sede":      "Ciencias Agropecuarias",
        "ubicacion":        "Calle 64b N 25-65, Manizales, Caldas",
        "capacidad_maxima": 290,
        "estado_activo":    True
    },
    {
        "nombre_sede":      "Sede Lans",
        "ubicacion":        "Av. Santander N 4142, Manizales, Caldas",
        "capacidad_maxima": 270,
        "estado_activo":    True
    }
]

HORARIO_DEFAULT = {"apertura": "11:00", "cierre": "15:00"}


def insertar_sedes():
    db = obtener_bd()
    crear_colecciones(db)

    col = db[Sede.coleccion]

    # Limpiar coleccion antes de reinsertar (opcional)
    col.delete_many({})
    print("Coleccion limpiada.")

    docs = []
    for datos in SEDES:
        sede = Sede(
            nombre_sede      = datos["nombre_sede"],
            ubicacion        = datos["ubicacion"],
            capacidad_maxima = datos["capacidad_maxima"],
            estado_activo    = datos["estado_activo"],
            horario_atencion = HORARIO_DEFAULT
        )
        docs.append(sede.to_dict())

    resultado = col.insert_many(docs)
    print(f"\nSedes insertadas: {len(resultado.inserted_ids)}")
    for i, _id in enumerate(resultado.inserted_ids):
        print(f"  [{i+1}] {SEDES[i]['nombre_sede']} -> _id: {_id}")

    return resultado.inserted_ids


if __name__ == "__main__":
    insertar_sedes()