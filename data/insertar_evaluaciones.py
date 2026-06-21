"""
insertar_evaluaciones.py
Genera e inserta documentos en Evaluaciones.
Toma estudiantes y sedes existentes de la BD.
No todos los estudiantes evaluan, simulamos un 40% de participacion.
"""

import random
from connection import obtener_bd
from models import Evaluacion, Estudiante, Sede

# ------------------------------------------------------------------
# Datos de referencia
# ------------------------------------------------------------------
COMENTARIOS_BUENOS = [
    "La comida estuvo muy buena, bien servida y caliente.",
    "Excelente atencion por parte del personal del comedor.",
    "La sopa del dia estuvo deliciosa, me gusto mucho.",
    "El plato principal estaba bien condimentado y la porcion generosa.",
    "Muy buen servicio, rapido y organizado.",
    "La comida es nutritiva y suficiente para rendir bien en clases.",
    "Me parecio un excelente servicio, el personal muy amable.",
    "El ambiente del comedor es comodo y limpio, me siento bien ahi.",
    "La variedad de jugos es buena, siempre hay opciones frescas.",
    "Todo estuvo perfecto, la comida rica y bien presentada."
]

COMENTARIOS_REGULARES = [
    "La comida estaba un poco fria pero el sabor era aceptable.",
    "El servicio fue algo lento hoy por la cantidad de estudiantes.",
    "La porcion podria ser un poco mas generosa.",
    "El sabor estuvo bien pero la presentacion puede mejorar.",
    "Regular, hay dias mejores y dias no tan buenos.",
    "La sopa estuvo bien pero el seco estaba algo seco.",
    "Aceptable, cumple con lo necesario pero puede mejorar.",
    "El servicio fue normal, sin nada destacable."
]

COMENTARIOS_MALOS = [
    "La comida llego fria y sin mucho sabor hoy.",
    "La atencion fue muy lenta, espere demasiado tiempo.",
    "El plato no estaba bien cocido, me decepciono.",
    "La porcion fue muy pequena para un almuerzo completo.",
    "No me gusto la comida de hoy, esperaba algo mejor.",
    "El comedor estaba muy lleno y el servicio se resintio.",
    "La comida de hoy no cumplio mis expectativas.",
    "Hubo problemas con la organizacion del servicio hoy."
]

SUGERENCIAS = [
    "Podrian agregar mas variedad de jugos naturales.",
    "Seria bueno tener opciones sin gluten disponibles.",
    "Me gustaria que hubiera mas fruta fresca de postre.",
    "Podrian mejorar la temperatura de la sopa al servirla.",
    "Seria util tener el menu publicado con anticipacion en la app.",
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

PERIODOS_FECHAS = {
    "2018-1": ("2018-01-22", "2018-06-15"),
    "2018-2": ("2018-07-23", "2018-11-30"),
    "2019-1": ("2019-01-21", "2019-06-14"),
    "2019-2": ("2019-07-22", "2019-11-29"),
    "2020-1": ("2020-01-20", "2020-06-12"),
    "2020-2": ("2020-07-20", "2020-11-27"),
    "2021-1": ("2021-01-18", "2021-06-11"),
    "2021-2": ("2021-07-19", "2021-11-26"),
    "2022-1": ("2022-01-17", "2022-06-10"),
    "2022-2": ("2022-07-18", "2022-11-25"),
    "2023-1": ("2023-01-16", "2023-06-09"),
    "2023-2": ("2023-07-17", "2023-11-24"),
    "2024-1": ("2024-01-15", "2024-06-07"),
    "2024-2": ("2024-07-15", "2024-11-22"),
    "2025-1": ("2025-01-20", "2025-06-13"),
    "2025-2": ("2025-07-21", "2025-11-28"),
    "2026-1": ("2026-01-19", "2026-06-12"),
}

BATCH_SIZE = 1000


def fecha_aleatoria_en_periodo(periodo):
    inicio, fin = PERIODOS_FECHAS[periodo]
    from datetime import date, timedelta
    d_inicio = date.fromisoformat(inicio)
    d_fin    = date.fromisoformat(fin)
    delta    = (d_fin - d_inicio).days
    return (d_inicio + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def elegir_comentario(calificacion):
    if calificacion >= 4:
        return random.choice(COMENTARIOS_BUENOS)
    elif calificacion == 3:
        return random.choice(COMENTARIOS_REGULARES)
    else:
        return random.choice(COMENTARIOS_MALOS)


def insertar_evaluaciones(participacion=0.40):
    db  = obtener_bd()
    col = db[Evaluacion.coleccion]

    # Traer estudiantes unicos por codigo (un representante por estudiante)
    print("Cargando estudiantes...")
    pipeline = [
        {"$group": {
            "_id": "$codigo_estudiante",
            "nombre_completo":       {"$first": "$nombre_completo"},
            "semestre":              {"$first": "$semestre"},
            "fecha_inicio_subsidio": {"$first": "$fecha_inicio_subsidio"},
            "fecha_fin_subsidio":    {"$first": "$fecha_fin_subsidio"},
            "sede_id":               {"$first": "$sede_id"},
            "periodo":               {"$first": "$periodo"}
        }}
    ]
    estudiantes = list(db[Estudiante.coleccion].aggregate(pipeline))

    if not estudiantes:
        print("ERROR: No hay estudiantes. Ejecuta insertar_estudiantes.py primero.")
        return

    # Seleccionar el % de participacion
    muestra = random.sample(estudiantes, int(len(estudiantes) * participacion))

    col.delete_many({})
    print("Coleccion Evaluaciones limpiada.")
    print(f"Estudiantes totales    : {len(estudiantes):,}")
    print(f"Participacion ({int(participacion*100)}%)  : {len(muestra):,} evaluaciones\n")

    batch      = []
    insertados = 0

    for est in muestra:
        periodo = est.get("periodo", "2024-1")

        embed_estudiante = {
            "nombre_completo":       est["nombre_completo"],
            "codigo_estudiante":     est["_id"],
            "semestre":              est.get("semestre", 1),
            "fecha_inicio_subsidio": est.get("fecha_inicio_subsidio", "2024-01-15"),
            "fecha_fin_subsidio":    est.get("fecha_fin_subsidio", "2024-06-07")
        }

        embed_sede = {
            "nombre_sede": est["sede_id"]["nombre_sede"]
        }

        calificacion = random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 10, 20, 35, 30]  # mas probabilidad de calificaciones altas
        )[0]

        evaluacion = Evaluacion(
            estudiante_id    = embed_estudiante,
            sede_id          = embed_sede,
            fecha_evaluacion = fecha_aleatoria_en_periodo(periodo),
            calificacion     = calificacion,
            comentario       = elegir_comentario(calificacion),
            sugerencias      = random.choice(SUGERENCIAS) if calificacion <= 3 else None
        )

        batch.append(evaluacion.to_dict())

        if len(batch) >= BATCH_SIZE:
            col.insert_many(batch)
            insertados += len(batch)
            print(f"  Insertados: {insertados:,}/{len(muestra):,} ({round(insertados/len(muestra)*100,1)}%)")
            batch = []

    if batch:
        col.insert_many(batch)
        insertados += len(batch)

    print(f"\nEvaluaciones insertadas: {insertados:,}")


if __name__ == "__main__":
    insertar_evaluaciones(participacion=0.40)