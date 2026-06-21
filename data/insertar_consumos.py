"""
insertar_consumos.py
Genera e inserta documentos en Consumos.
45 consumos por sede por dia habil (lunes-viernes sin festivos)
dentro de los semestres academicos definidos (2018-1 a 2026-1).
Cada consumo toma un estudiante real de la BD y verifica coherencia
entre tipo_almuerzo del estudiante y tipo_comida del menu del dia.
"""

import random
from datetime import date, timedelta, datetime
from connection import obtener_bd
from models import Consumo, Estudiante, Sede, Menu

# ------------------------------------------------------------------
# Semestres academicos (mismo rango usado en insertar_menus.py)
# ------------------------------------------------------------------
SEMESTRES = {
    "2018-1": (datetime(2018, 1, 22), datetime(2018, 6, 15)),
    "2018-2": (datetime(2018, 7, 23), datetime(2018, 11, 30)),
    "2019-1": (datetime(2019, 1, 21), datetime(2019, 6, 14)),
    "2019-2": (datetime(2019, 7, 22), datetime(2019, 11, 29)),
    "2020-1": (datetime(2020, 1, 20), datetime(2020, 6, 12)),
    "2020-2": (datetime(2020, 7, 20), datetime(2020, 11, 27)),
    "2021-1": (datetime(2021, 1, 18), datetime(2021, 6, 11)),
    "2021-2": (datetime(2021, 7, 19), datetime(2021, 11, 26)),
    "2022-1": (datetime(2022, 1, 17), datetime(2022, 6, 10)),
    "2022-2": (datetime(2022, 7, 18), datetime(2022, 11, 25)),
    "2023-1": (datetime(2023, 1, 16), datetime(2023, 6, 9)),
    "2023-2": (datetime(2023, 7, 17), datetime(2023, 11, 24)),
    "2024-1": (datetime(2024, 1, 15), datetime(2024, 6, 7)),
    "2024-2": (datetime(2024, 7, 15), datetime(2024, 11, 22)),
    "2025-1": (datetime(2025, 1, 20), datetime(2025, 6, 13)),
    "2025-2": (datetime(2025, 7, 21), datetime(2025, 11, 28)),
    "2026-1": (datetime(2026, 1, 19), datetime(2026, 7, 10)),
}

# ------------------------------------------------------------------
# Festivos Colombia 2018-2026 (mismo set usado en insertar_menus.py)
# ------------------------------------------------------------------
FESTIVOS = set([
    date(2018,1,1), date(2018,1,8), date(2018,3,19), date(2018,3,29), date(2018,3,30),
    date(2018,5,1), date(2018,5,14), date(2018,6,4), date(2018,6,11), date(2018,7,2),
    date(2018,7,20), date(2018,8,7), date(2018,8,20), date(2018,10,15), date(2018,11,5),
    date(2018,11,12), date(2018,12,8), date(2018,12,25),
    date(2019,1,1), date(2019,1,7), date(2019,3,25), date(2019,4,18), date(2019,4,19),
    date(2019,5,1), date(2019,6,3), date(2019,6,24), date(2019,7,1), date(2019,7,20),
    date(2019,8,7), date(2019,8,19), date(2019,10,14), date(2019,11,4), date(2019,11,11),
    date(2019,12,8), date(2019,12,25),
    date(2020,1,1), date(2020,1,6), date(2020,3,23), date(2020,4,9), date(2020,4,10),
    date(2020,5,1), date(2020,5,25), date(2020,6,15), date(2020,6,22), date(2020,6,29),
    date(2020,7,20), date(2020,8,7), date(2020,8,17), date(2020,10,12), date(2020,11,2),
    date(2020,11,16), date(2020,12,8), date(2020,12,25),
    date(2021,1,1), date(2021,1,11), date(2021,3,22), date(2021,4,1), date(2021,4,2),
    date(2021,5,1), date(2021,5,17), date(2021,6,7), date(2021,6,14), date(2021,7,5),
    date(2021,7,20), date(2021,8,7), date(2021,8,16), date(2021,10,18), date(2021,11,1),
    date(2021,11,15), date(2021,12,8), date(2021,12,25),
    date(2022,1,1), date(2022,1,10), date(2022,3,21), date(2022,4,14), date(2022,4,15),
    date(2022,5,1), date(2022,5,30), date(2022,6,20), date(2022,6,27), date(2022,7,4),
    date(2022,7,20), date(2022,8,7), date(2022,8,15), date(2022,10,17), date(2022,11,7),
    date(2022,11,14), date(2022,12,8), date(2022,12,25),
    date(2023,1,1), date(2023,1,9), date(2023,3,20), date(2023,4,6), date(2023,4,7),
    date(2023,5,1), date(2023,5,22), date(2023,6,12), date(2023,6,19), date(2023,7,3),
    date(2023,7,20), date(2023,8,7), date(2023,8,21), date(2023,10,16), date(2023,11,6),
    date(2023,11,13), date(2023,12,8), date(2023,12,25),
    date(2024,1,1), date(2024,1,8), date(2024,3,25), date(2024,3,28), date(2024,3,29),
    date(2024,5,1), date(2024,5,13), date(2024,6,3), date(2024,6,10), date(2024,7,1),
    date(2024,7,20), date(2024,8,7), date(2024,8,19), date(2024,10,14), date(2024,11,4),
    date(2024,11,11), date(2024,12,8), date(2024,12,25),
    date(2025,1,1), date(2025,1,6), date(2025,3,24), date(2025,4,17), date(2025,4,18),
    date(2025,5,1), date(2025,6,2), date(2025,6,23), date(2025,6,30), date(2025,7,21),
    date(2025,7,20), date(2025,8,7), date(2025,8,18), date(2025,10,13), date(2025,11,3),
    date(2025,11,17), date(2025,12,8), date(2025,12,25),
    date(2026,1,1), date(2026,1,12), date(2026,3,23), date(2026,4,2), date(2026,4,3),
    date(2026,5,1), date(2026,5,18), date(2026,6,8), date(2026,6,15), date(2026,6,29),
])

# === AJUSTE PARA LLEGAR AL LÍMITE ===
CONSUMOS_POR_SEDE_DIA = 45   # antes 245
BATCH_SIZE             = 1000

HORAS_INGRESO = [
    "11:00", "11:10", "11:20", "11:30", "11:40", "11:50",
    "12:00", "12:10", "12:20", "12:30", "12:40", "12:50",
    "13:00", "13:10", "13:20", "13:30", "13:40", "13:50",
    "14:00", "14:10", "14:20", "14:30", "14:40", "14:50"
]


def generar_fechas_habiles_por_semestres(semestres):
    """Genera todas las fechas habiles (sin festivos) que caen dentro de
    cualquier semestre definido, igual que en insertar_menus.py."""
    fechas = set()
    for periodo, (inicio, fin) in semestres.items():
        actual = inicio
        while actual <= fin:
            if actual.weekday() < 5 and actual.date() not in FESTIVOS:
                fechas.add(actual)
            actual += timedelta(days=1)
    return sorted(fechas)


def insertar_consumos():
    db = obtener_bd()
    col = db[Consumo.coleccion]

    # ------------------------------------------------------------------
    # Cargar estudiantes unicos con su tipo_almuerzo
    # ------------------------------------------------------------------
    print("Cargando estudiantes de la BD...")
    pipeline_est = [
        {"$group": {
            "_id":               "$codigo_estudiante",
            "nombre_completo":   {"$first": "$nombre_completo"},
            "tipo_almuerzo":     {"$first": "$tipo_almuerzo"},
        }}
    ]
    estudiantes_raw = list(db[Estudiante.coleccion].aggregate(pipeline_est, allowDiskUse=True))

    if not estudiantes_raw:
        print("ERROR: No hay estudiantes. Ejecuta insertar_estudiantes.py primero.")
        return

    estudiantes = [
        {
            "codigo_estudiante": e["_id"],
            "nombre_completo":   e["nombre_completo"],
            "tipo_almuerzo":     e.get("tipo_almuerzo")
        }
        for e in estudiantes_raw
    ]

    est_carnivoro   = [e for e in estudiantes if e.get("tipo_almuerzo") == "carnivoro"]
    est_vegetariano = [e for e in estudiantes if e.get("tipo_almuerzo") == "vegetariano"]
    print(f"  Estudiantes unicos total: {len(estudiantes):,}")
    print(f"  Carnivoros  : {len(est_carnivoro):,}")
    print(f"  Vegetarianos: {len(est_vegetariano):,}")

    # ------------------------------------------------------------------
    # Cargar sedes
    # ------------------------------------------------------------------
    sedes = list(db[Sede.coleccion].find({}, {"_id": 1, "nombre_sede": 1, "ubicacion": 1}))
    if not sedes:
        print("ERROR: No hay sedes. Ejecuta insertar_sedes.py primero.")
        return
    print(f"  Sedes cargadas: {len(sedes)}")

    # ------------------------------------------------------------------
    # Cargar menus indexados por (nombre_sede, fecha, tipo_comida)
    # ------------------------------------------------------------------
    print("Cargando menus de la BD (puede tomar un momento)...")
    menus_index = {}

    cursor = db[Menu.coleccion].find(
        {},
        {"sede_id": 1, "fecha": 1, "tipo_comida": 1, "plato": 1}
    )
    for m in cursor:
        sede_ref = m.get("sede_id")
        if isinstance(sede_ref, dict):
            nombre_sede_key = sede_ref.get("nombre_sede", "")
        else:
            nombre_sede_key = str(sede_ref)

        fecha_raw = m.get("fecha", "")
        if hasattr(fecha_raw, "strftime"):
            fecha_key = fecha_raw.strftime("%Y-%m-%d")
        else:
            fecha_key = str(fecha_raw)

        tipo_key = m.get("tipo_comida", "")
        menus_index[(nombre_sede_key, fecha_key, tipo_key)] = {
            "plato":       m.get("plato", ""),
            "tipo_comida": tipo_key
        }

    print(f"  Menus indexados: {len(menus_index):,}")

    # ------------------------------------------------------------------
    # Generar consumos
    # ------------------------------------------------------------------
    col.delete_many({})
    print("Coleccion Consumos limpiada.")

    fechas    = generar_fechas_habiles_por_semestres(SEMESTRES)
    total_est = len(fechas) * len(sedes) * CONSUMOS_POR_SEDE_DIA
    print(f"\nDias habiles (dentro de semestres): {len(fechas):,}")
    print(f"Sedes          : {len(sedes)}")
    print(f"Consumos/sede  : {CONSUMOS_POR_SEDE_DIA}")
    print(f"Total estimado : {total_est:,}\n")

    batch      = []
    insertados = 0
    sin_menu   = 0

    for fecha_dt in fechas:
        fecha_str = fecha_dt.strftime("%Y-%m-%d")

        for sede in sedes:
            nombre_sede = sede["nombre_sede"]
            embed_sede = {
                "nombre_sede": nombre_sede,
                "ubicacion":   sede.get("ubicacion", "")
            }

            menu_carn = menus_index.get((nombre_sede, fecha_str, "carnivoro"))
            menu_veg  = menus_index.get((nombre_sede, fecha_str, "vegetariano"))

            for _ in range(CONSUMOS_POR_SEDE_DIA):
                if menu_carn and menu_veg:
                    tipo = random.choice(["carnivoro", "vegetariano"])
                elif menu_carn:
                    tipo = "carnivoro"
                elif menu_veg:
                    tipo = "vegetariano"
                else:
                    tipo = random.choice(["carnivoro", "vegetariano"])
                    sin_menu += 1

                pool = est_carnivoro if tipo == "carnivoro" else est_vegetariano
                if not pool:
                    pool = estudiantes
                est = random.choice(pool)

                embed_estudiante = {
                    "nombre_completo":   est["nombre_completo"],
                    "codigo_estudiante": est["codigo_estudiante"],
                    "tipo_almuerzo":     est.get("tipo_almuerzo", tipo)
                }

                menu = menus_index.get((nombre_sede, fecha_str, tipo))
                embed_menu = menu if menu else {
                    "plato":       "Menu no disponible",
                    "tipo_comida": tipo
                }

                consumo = Consumo(
                    estudiante_id        = embed_estudiante,
                    sede_id              = embed_sede,
                    menu_id              = embed_menu,
                    fecha_consumo        = fecha_dt,
                    hora_ingreso         = random.choice(HORAS_INGRESO),
                    validacion_identidad = random.random() > 0.02
                )

                batch.append(consumo.to_dict())

                if len(batch) >= BATCH_SIZE:
                    col.insert_many(batch)
                    insertados += len(batch)
                    pct = round(insertados / total_est * 100, 1)
                    print(f"  Insertados: {insertados:,}/{total_est:,} ({pct}%)")
                    batch = []

    if batch:
        col.insert_many(batch)
        insertados += len(batch)

    print(f"\nConsumos insertados: {insertados:,}")
    if sin_menu:
        print(f"Consumos sin menu disponible ese dia/sede: {sin_menu:,}")


if __name__ == "__main__":
    insertar_consumos()