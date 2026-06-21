"""
insertar_estudiantes.py
Genera documentos en Estudiantes.
Pool de ~58,900 estudiantes unicos x hasta 17 semestres (2018-1 al 2026-1).
Cada estudiante cursa entre 1 y 12 semestres (duracion real de una
carrera), empezando en un periodo aleatorio dentro del rango.

NOTA: sede_id se usa solo internamente para distribuir el pool de
estudiantes (no se guarda en el documento, ya que el modelo Estudiante
no define ese campo). El vinculo estudiante-sede real se maneja en
otras colecciones como consumos.
"""

import random
from datetime import datetime
from connection import obtener_bd
from models import Estudiante, Sede

# ------------------------------------------------------------------
# Semestres y fechas de inicio/fin (como datetime)
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
PERIODOS = list(SEMESTRES.keys())  # 17 periodos, en orden cronologico
HOY = datetime(2026, 6, 20)  # fecha de referencia para subsidio vigente

# ------------------------------------------------------------------
# Datos de referencia (ampliados para reducir repeticion visual)
# ------------------------------------------------------------------
NOMBRES = [
    "Santiago","Valentina","Juan David","Maria Camila","Andres Felipe",
    "Laura Melissa","Carlos Mario","Sara Isabel","Miguel Angel","Diana Marcela",
    "Daniel Esteban","Manuela","Sebastian","Alejandra","Felipe","Natalia",
    "Jhon Alexander","Paula Andrea","Luis Fernando","Monica","Ricardo",
    "Catalina","Hector","Adriana","Jorge","Stephanie","Ivan","Lina Maria",
    "Camilo","Carolina","Fabian","Marcela","Andres","Juliana","David",
    "Angelica","Nicolas","Leidy","Cristian","Yuliana","Harold","Paola",
    "Edwin","Jennifer","Oscar","Liliana","Mario","Gloria","Jairo","Viviana",
    "Esteban","Tatiana","Mauricio","Alejandro","Daniela","Sergio","Yesica",
    "Wilmer","Diego","Maria Fernanda","Johan","Yuliana Andrea","Brayan",
    "Karen","Anderson","Maria Jose","Cristian Camilo","Lorena","Yeison",
    "Vanessa","Wilson","Astrid","Ferney","Dayana","Yulieth","Heider",
    "Ximena","Robinson","Carol","Geraldine","Albeiro","Sandra","Norbey",
    "Maritza","Yeferson","Erika","Albert","Yulisa","Didier","Marcia",
    "Jhonatan","Maria Alejandra","Luis Carlos","Yenny","Faber","Tania"
]

APELLIDOS = [
    "Garcia","Rodriguez","Martinez","Lopez","Gonzalez","Perez","Sanchez",
    "Ramirez","Torres","Flores","Rivera","Gomez","Diaz","Morales","Jimenez",
    "Herrera","Mendoza","Castillo","Vargas","Romero","Rios","Alvarez","Guerrero",
    "Ortiz","Silva","Rojas","Cardenas","Osorio","Zapata","Cano","Restrepo",
    "Aguirre","Palacios","Soto","Cruz","Ramos","Duran","Acosta","Medina",
    "Suarez","Betancur","Hurtado","Giraldo","Velez","Arango","Mejia","Salazar",
    "Montoya","Bedoya","Ocampo","Quintero","Marin","Hincapie","Henao","Vasquez",
    "Carmona","Calderon","Valencia","Gallego","Higuita","Correa","Loaiza",
    "Tabares","Echeverri","Trujillo","Patino","Pineda","Naranjo","Velasquez",
    "Buitrago","Cifuentes","Londono","Sepulveda","Castano","Marulanda",
    "Granada","Largo","Villada","Quiceno","Yepes","Aristizabal","Bermudez",
    "Cuartas","Estrada","Franco","Gaviria","Idarraga","Jaramillo","Ladino",
    "Mazo","Noreña","Orozco","Parra","Quintana","Rendon","Saldarriaga"
]

FACULTADES = [
    "Ingenieria",
    "Ciencias Exactas y Naturales",
    "Ciencias Agropecuarias",
    "Ciencias para la Salud",
    "Artes y Humanidades",
    "Ciencias Juridicas y Sociales",
    "Administracion"
]

PROGRAMAS = {
    "Ingenieria":                    ["Ingenieria de Sistemas", "Ingenieria Civil", "Ingenieria Electronica", "Ingenieria Industrial"],
    "Ciencias Exactas y Naturales":  ["Matematicas", "Fisica", "Quimica", "Biologia"],
    "Ciencias Agropecuarias":        ["Medicina Veterinaria", "Agronomia", "Zootecnia"],
    "Ciencias para la Salud":        ["Medicina", "Enfermeria", "Bacteriologia", "Nutricion y Dietetica"],
    "Artes y Humanidades":           ["Bellas Artes", "Filosofia", "Historia", "Linguistica"],
    "Ciencias Juridicas y Sociales": ["Derecho", "Trabajo Social", "Sociologia"],
    "Administracion":                ["Administracion de Empresas", "Contaduria Publica", "Economia"]
}

TIPO_ALMUERZO = ["carnivoro", "vegetariano"]

BATCH_SIZE = 1000


def generar_codigo(numero):
    """Codigo de 11 digitos con prefijo 00000 como en el carne."""
    return f"00000{str(numero).zfill(6)}"


def generar_correo(nombre, apellido, numero):
    nombre_clean   = nombre.lower().replace(" ", "").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    apellido_clean = apellido.lower().replace(" ", "").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    return f"{nombre_clean}.{apellido_clean}{numero}@ucaldas.edu.co"


def insertar_estudiantes():
    db    = obtener_bd()
    col   = db[Estudiante.coleccion]
    sedes = list(db[Sede.coleccion].find({}, {"_id": 1, "nombre_sede": 1}))

    if not sedes:
        print("ERROR: No hay sedes. Ejecuta insertar_sedes.py primero.")
        return

    col.delete_many({})
    print("Coleccion Estudiantes limpiada.")

    BLOQUES_DE_GENERACION = 5      # cuantos lotes de poblacion se generan
    TAMANO_BLOQUE = 25000          # estudiantes unicos generados por bloque
    total_periodos = len(PERIODOS)

    # Estimado real (varia porque cada estudiante dura entre 1 y 12 semestres,
    # con 50% completando carrera larga de 8-12 semestres)
    promedio_semestres_estimado = 8.27
    total_est_aprox = int(BLOQUES_DE_GENERACION * TAMANO_BLOQUE * promedio_semestres_estimado)

    print(f"Estudiantes unicos por bloque : {TAMANO_BLOQUE:,}")
    print(f"Bloques de generacion         : {BLOQUES_DE_GENERACION}")
    print(f"Periodos disponibles          : {total_periodos}")
    print(f"Duracion por estudiante       : 1 a 12 semestres (50% completa carrera larga 8-12)")
    print(f"Total estimado (aproximado)   : {total_est_aprox:,} documentos\n")

    batch      = []
    insertados = 0
    codigo_num = 100000  # numero base para codigos

    for bloque in range(BLOQUES_DE_GENERACION):
        for i in range(TAMANO_BLOQUE):
            codigo_num += 1

            # Datos fijos del estudiante (no cambian entre semestres)
            nombre    = random.choice(NOMBRES)
            apellido1 = random.choice(APELLIDOS)
            apellido2 = random.choice(APELLIDOS)
            nombre_completo = f"{nombre} {apellido1} {apellido2}"
            codigo    = generar_codigo(codigo_num)
            correo    = generar_correo(nombre, apellido1, codigo_num)
            telefono  = f"3{random.randint(100000000, 999999999)}"
            facultad  = random.choice(FACULTADES)
            programa  = random.choice(PROGRAMAS[facultad])
            estrato   = random.randint(1, 3)  # subsidio aplica estratos 1-3
            tipo      = random.choice(TIPO_ALMUERZO)

            # Duracion real de la carrera: 50% completa carrera larga (8-12
            # semestres, reclamando el subsidio casi toda la carrera),
            # 50% duracion variada (1-12, entradas/salidas mas tempranas)
            if random.random() < 0.5:
                duracion = random.randint(8, 12)
            else:
                duracion = random.randint(1, 12)

            # Periodo de inicio aleatorio, recortando si no le alcanzan
            # los periodos restantes para completar su duracion
            max_inicio_idx = max(0, total_periodos - duracion)
            idx_inicio = random.randint(0, max_inicio_idx)

            # En que semestre academico (1-12) inicio su carrera
            semestre_academico_inicio = random.randint(1, max(1, 12 - duracion + 1))

            for offset in range(duracion):
                idx_periodo = idx_inicio + offset
                periodo = PERIODOS[idx_periodo]
                fecha_inicio, fecha_fin = SEMESTRES[periodo]

                semestre_actual = min(12, semestre_academico_inicio + offset)

                # subsidio_activo refleja el estado VIGENTE respecto a hoy
                # (20 de junio 2026): solo esta activo si la fecha de hoy
                # cae dentro del rango [fecha_inicio, fecha_fin] de ese
                # semestre especifico. Semestres ya cerrados o futuros
                # quedan en false.
                subsidio_activo = fecha_inicio <= HOY <= fecha_fin

                estudiante = Estudiante(
                    codigo_estudiante     = codigo,
                    nombre_completo       = nombre_completo,
                    correo                = correo,
                    telefono              = telefono,
                    facultad              = facultad,
                    programa              = programa,
                    semestre              = semestre_actual,
                    estrato               = estrato,
                    fecha_inicio_subsidio = fecha_inicio,
                    fecha_fin_subsidio    = fecha_fin,
                    tipo_almuerzo         = tipo,
                    subsidio_activo       = subsidio_activo
                )

                doc = estudiante.to_dict()
                batch.append(doc)

                if len(batch) >= BATCH_SIZE:
                    col.insert_many(batch)
                    insertados += len(batch)
                    print(f"  Insertados: {insertados:,}")
                    batch = []

    if batch:
        col.insert_many(batch)
        insertados += len(batch)

    print(f"\nEstudiantes insertados: {insertados:,}")


if __name__ == "__main__":
    insertar_estudiantes()