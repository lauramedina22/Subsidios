"""
insertar_evaluaciones.py
Genera e inserta documentos en Evaluaciones.
Toma estudiantes reales de la BD (insertados con insertar_estudiantes.py).
50% de los estudiantes unicos participan; cada uno genera entre 1 y 15
evaluaciones (promedio ~8), total esperado ~200,000 evaluaciones.
Las fechas (fecha_evaluacion, fecha_inicio_subsidio, fecha_fin_subsidio)
se manejan como datetime real, consistente con estudiantes y consumos.
"""

import random
from datetime import date, datetime, timedelta
from connection import obtener_bd
from models import Evaluacion, Estudiante, Sede, Menu

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

# ------------------------------------------------------------------
# Plantillas de comentarios (todas referencian el plato especifico)
# ------------------------------------------------------------------
COMENTARIOS_BUENOS = [
    "{plato} estuvo muy bueno, bien servido y caliente.",
    "Excelente atencion del personal al servir {plato}.",
    "{plato} estuvo delicioso, me gusto mucho hoy.",
    "{plato} estaba bien condimentado y la porcion generosa.",
    "Muy buen servicio hoy, {plato} llego rapido y caliente.",
    "{plato} es nutritivo y me dejo satisfecho para rendir en clases.",
    "El personal fue muy amable al servir {plato}.",
    "Comi {plato} en un ambiente comodo y limpio, todo perfecto.",
    "{plato} vino acompañado de un jugo fresco, excelente combinacion.",
    "{plato} estuvo perfecto, rico y bien presentado."
]

COMENTARIOS_REGULARES = [
    "{plato} estaba un poco frio pero el sabor era aceptable.",
    "El servicio fue algo lento hoy al servir {plato}, por la cantidad de estudiantes.",
    "La porcion de {plato} podria ser un poco mas generosa.",
    "{plato} tenia buen sabor pero la presentacion puede mejorar.",
    "{plato} estuvo regular, hay dias mejores y dias no tan buenos.",
    "{plato} tenia la sopa bien pero el seco estaba algo seco.",
    "{plato} fue aceptable, cumple con lo necesario pero puede mejorar.",
    "El servicio de {plato} fue normal, sin nada destacable."
]

COMENTARIOS_MALOS = [
    "{plato} llego frio y sin mucho sabor hoy.",
    "La atencion para servir {plato} fue muy lenta, espere demasiado tiempo.",
    "{plato} no estaba bien cocido, me decepciono.",
    "La porcion de {plato} fue muy pequena para un almuerzo completo.",
    "No me gusto {plato} de hoy, esperaba algo mejor.",
    "El comedor estaba muy lleno cuando sirvieron {plato} y el servicio se resintio.",
    "{plato} de hoy no cumplio mis expectativas.",
    "Hubo problemas con la organizacion del servicio al repartir {plato}."
]

SUGERENCIAS = [
    "Podrian agregar mas variedad de jugos naturales.",
    "Seria bueno tener opciones sin gluten disponibles.",
    "Me gustaria que hubiera mas fruta fresca de postre.",
    "Podrian mejorar la temperatura de la sopa al servirla.",
    "Seria util tener el menu publicado con anticipacion.",
    "Podrian agregar mas opciones vegetarianas durante la semana.",
    "El espacio del comedor podria ampliarse para evitar filas largas.",
    "Seria bueno tener mas personal en las horas pico.",
    "Podrian rotar mas los platos para no repetir tanto en la semana.",
    "Me gustaria que se publicara la informacion nutricional visible.",
    "Seria ideal tener un sistema de turnos para evitar aglomeraciones.",
    "Podrian mejorar la iluminacion del comedor.",
    "Seria bueno tener opciones de ensalada mas variadas.",
    "Podrian considerar agregar una opcion de postre al almuerzo."
]

BATCH_SIZE = 1000
MIN_EVALUACIONES_POR_ESTUDIANTE = 1
MAX_EVALUACIONES_POR_ESTUDIANTE = 15   # antes 25


def es_dia_habil(fecha_dt):
    return fecha_dt.weekday() < 5 and fecha_dt.date() not in FESTIVOS


def fecha_habil_aleatoria_entre(dt_inicio, dt_fin, intentos_max=30):
    """Fecha datetime aleatoria habil (lunes-viernes, sin festivos)
    entre dos fechas. Si tras varios intentos no encuentra una habil,
    devuelve la mejor aproximacion encontrada."""
    d_inicio = dt_inicio.date() if hasattr(dt_inicio, 'date') else dt_inicio
    d_fin    = dt_fin.date()    if hasattr(dt_fin,    'date') else dt_fin
    delta    = (d_fin - d_inicio).days
    if delta <= 0:
        elegido = d_inicio
        return datetime(elegido.year, elegido.month, elegido.day)

    for _ in range(intentos_max):
        candidato = d_inicio + timedelta(days=random.randint(0, delta))
        candidato_dt = datetime(candidato.year, candidato.month, candidato.day)
        if es_dia_habil(candidato_dt):
            return candidato_dt

    actual = d_inicio
    while actual <= d_fin:
        actual_dt = datetime(actual.year, actual.month, actual.day)
        if es_dia_habil(actual_dt):
            return actual_dt
        actual += timedelta(days=1)
    return datetime(d_inicio.year, d_inicio.month, d_inicio.day)


def elegir_comentario(calificacion, plato):
    if calificacion >= 4:
        plantilla = random.choice(COMENTARIOS_BUENOS)
    elif calificacion == 3:
        plantilla = random.choice(COMENTARIOS_REGULARES)
    else:
        plantilla = random.choice(COMENTARIOS_MALOS)
    return plantilla.format(plato=plato)


def insertar_evaluaciones(participacion=0.50):   # antes 0.40
    db  = obtener_bd()
    col = db[Evaluacion.coleccion]

    col.drop()
    db.create_collection(Evaluacion.coleccion, validator=Evaluacion.schema)
    print("Colección Evaluaciones recreada con el schema actual.")

    print("Cargando estudiantes unicos de la BD...")
    pipeline = [
        {"$group": {
            "_id":                    "$codigo_estudiante",
            "nombre_completo":        {"$first": "$nombre_completo"},
            "semestre":               {"$max":   "$semestre"},
            "fecha_inicio_subsidio":  {"$first": "$fecha_inicio_subsidio"},
            "fecha_fin_subsidio":     {"$first": "$fecha_fin_subsidio"},
        }}
    ]
    estudiantes = list(db[Estudiante.coleccion].aggregate(pipeline, allowDiskUse=True))

    if not estudiantes:
        print("ERROR: No hay estudiantes. Ejecuta insertar_estudiantes.py primero.")
        return

    sedes = list(db[Sede.coleccion].find({}, {"nombre_sede": 1, "ubicacion": 1}))
    if not sedes:
        print("ERROR: No hay sedes. Ejecuta insertar_sedes.py primero.")
        return

    print("Cargando menus de la BD para vincular platos...")
    menus_index = {}
    cursor = db[Menu.coleccion].find({}, {"sede_id": 1, "fecha": 1, "tipo_comida": 1, "plato": 1})
    for m in cursor:
        sede_ref = m.get("sede_id")
        nombre_sede_key = sede_ref.get("nombre_sede", "") if isinstance(sede_ref, dict) else str(sede_ref)
        fecha_raw = m.get("fecha")
        fecha_key = fecha_raw.strftime("%Y-%m-%d") if hasattr(fecha_raw, "strftime") else str(fecha_raw)
        tipo_key = m.get("tipo_comida", "")
        menus_index[(nombre_sede_key, fecha_key, tipo_key)] = {
            "plato":       m.get("plato", ""),
            "tipo_comida": tipo_key
        }
    print(f"  Menus indexados: {len(menus_index):,}\n")

    muestra = random.sample(estudiantes, int(len(estudiantes) * participacion))

    print(f"Estudiantes unicos en BD       : {len(estudiantes):,}")
    print(f"Participacion ({int(participacion*100)}%)          : {len(muestra):,} estudiantes")
    print(f"Evaluaciones por estudiante    : {MIN_EVALUACIONES_POR_ESTUDIANTE} a {MAX_EVALUACIONES_POR_ESTUDIANTE} (aleatorio)\n")

    batch      = []
    insertados = 0

    for est in muestra:
        fecha_inicio = est.get("fecha_inicio_subsidio") or date(2024, 1, 15)
        fecha_fin    = est.get("fecha_fin_subsidio")    or date(2024, 6, 7)

        embed_estudiante = {
            "nombre_completo":       est["nombre_completo"],
            "codigo_estudiante":     est["_id"],
            "semestre":              est.get("semestre", 1),
            "fecha_inicio_subsidio": fecha_inicio,
            "fecha_fin_subsidio":    fecha_fin
        }

        n_evaluaciones = random.randint(MIN_EVALUACIONES_POR_ESTUDIANTE, MAX_EVALUACIONES_POR_ESTUDIANTE)

        for _ in range(n_evaluaciones):
            menu = None
            embed_sede = None
            fecha_eval = None
            for _intento in range(15):
                sede_candidata = random.choice(sedes)
                fecha_candidata = fecha_habil_aleatoria_entre(fecha_inicio, fecha_fin)
                fecha_str = fecha_candidata.strftime("%Y-%m-%d")
                tipo_buscado = random.choice(["carnivoro", "vegetariano"])
                m = menus_index.get((sede_candidata["nombre_sede"], fecha_str, tipo_buscado))
                if m:
                    menu = m
                    embed_sede = {
                        "nombre_sede": sede_candidata["nombre_sede"],
                        "ubicacion":   sede_candidata["ubicacion"]
                    }
                    fecha_eval = fecha_candidata
                    break

            if menu is None:
                sede_candidata = random.choice(sedes)
                embed_sede = {
                    "nombre_sede": sede_candidata["nombre_sede"],
                    "ubicacion":   sede_candidata["ubicacion"]
                }
                fecha_eval = fecha_habil_aleatoria_entre(fecha_inicio, fecha_fin)
                menu = {"plato": "Plato no disponible", "tipo_comida": "carnivoro"}

            calificacion = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 20, 35, 30]
            )[0]

            evaluacion = Evaluacion(
                estudiante_id    = embed_estudiante,
                sede_id          = embed_sede,
                menu_id          = menu,
                fecha_evaluacion = fecha_eval,
                calificacion     = calificacion,
                comentario       = elegir_comentario(calificacion, menu["plato"]),
                sugerencias      = random.choice(SUGERENCIAS) if calificacion <= 3 else None
            )

            batch.append(evaluacion.to_dict())

            if len(batch) >= BATCH_SIZE:
                col.insert_many(batch)
                insertados += len(batch)
                print(f"  Insertados: {insertados:,}")
                batch = []

    if batch:
        col.insert_many(batch)
        insertados += len(batch)

    print(f"\nEvaluaciones insertadas: {insertados:,}")


if __name__ == "__main__":
    insertar_evaluaciones(participacion=0.50)