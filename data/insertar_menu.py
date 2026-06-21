"""
insertar_menus.py
Genera e inserta documentos en Menus_Diarios.
Por cada dia habil (lunes-viernes, sin festivos colombianos)
entre 2020-01-01 y 2026-06-30, y por cada sede,
se crean 2 menus: uno carnivoro y uno vegetariano.
"""

import random
from datetime import date, datetime, timedelta
from connection import obtener_bd
from models import Menu, Sede

# ------------------------------------------------------------------
# Festivos Colombia 2020-2026
# ------------------------------------------------------------------
FESTIVOS = set([
    # 2020
    date(2020,1,1), date(2020,1,6), date(2020,3,23), date(2020,4,9), date(2020,4,10),
    date(2020,5,1), date(2020,5,25), date(2020,6,15), date(2020,6,22), date(2020,6,29),
    date(2020,7,20), date(2020,8,7), date(2020,8,17), date(2020,10,12), date(2020,11,2),
    date(2020,11,16), date(2020,12,8), date(2020,12,25),
    # 2021
    date(2021,1,1), date(2021,1,11), date(2021,3,22), date(2021,4,1), date(2021,4,2),
    date(2021,5,1), date(2021,5,17), date(2021,6,7), date(2021,6,14), date(2021,7,5),
    date(2021,7,20), date(2021,8,7), date(2021,8,16), date(2021,10,18), date(2021,11,1),
    date(2021,11,15), date(2021,12,8), date(2021,12,25),
    # 2022
    date(2022,1,1), date(2022,1,10), date(2022,3,21), date(2022,4,14), date(2022,4,15),
    date(2022,5,1), date(2022,5,30), date(2022,6,20), date(2022,6,27), date(2022,7,4),
    date(2022,7,20), date(2022,8,7), date(2022,8,15), date(2022,10,17), date(2022,11,7),
    date(2022,11,14), date(2022,12,8), date(2022,12,25),
    # 2023
    date(2023,1,1), date(2023,1,9), date(2023,3,20), date(2023,4,6), date(2023,4,7),
    date(2023,5,1), date(2023,5,22), date(2023,6,12), date(2023,6,19), date(2023,7,3),
    date(2023,7,20), date(2023,8,7), date(2023,8,21), date(2023,10,16), date(2023,11,6),
    date(2023,11,13), date(2023,12,8), date(2023,12,25),
    # 2024
    date(2024,1,1), date(2024,1,8), date(2024,3,25), date(2024,3,28), date(2024,3,29),
    date(2024,5,1), date(2024,5,13), date(2024,6,3), date(2024,6,10), date(2024,7,1),
    date(2024,7,20), date(2024,8,7), date(2024,8,19), date(2024,10,14), date(2024,11,4),
    date(2024,11,11), date(2024,12,8), date(2024,12,25),
    # 2025
    date(2025,1,1), date(2025,1,6), date(2025,3,24), date(2025,4,17), date(2025,4,18),
    date(2025,5,1), date(2025,6,2), date(2025,6,23), date(2025,6,30), date(2025,7,21),
    date(2025,7,20), date(2025,8,7), date(2025,8,18), date(2025,10,13), date(2025,11,3),
    date(2025,11,17), date(2025,12,8), date(2025,12,25),
    # 2026
    date(2026,1,1), date(2026,1,12), date(2026,3,23), date(2026,4,2), date(2026,4,3),
    date(2026,5,1), date(2026,5,18), date(2026,6,8), date(2026,6,15), date(2026,6,29),
])

# ------------------------------------------------------------------
# Sopas carnivoro
# ------------------------------------------------------------------
SOPAS_CARNIVORO = [
    "Sopa de pasta con costilla de res",
    "Sancocho de gallina con papa y mazorca",
    "Sopa de arroz con pollo desmenuzado",
    "Caldo de costilla con papa y yuca",
    "Sopa de fideos con carne molida",
    "Mondongo con papa y zanahoria",
    "Sopa de cebada con espinazo de cerdo",
    "Ajiaco con pollo y mazorca",
    "Sopa de lentejas con tocino ahumado",
    "Sopa de arveja con cerdo",
    "Cazuela de res con platano verde",
    "Sopa de guineo con costilla",
    "Sopa de papa con pollo y cilantro",
    "Caldo de pata con garbanzos",
    "Sopa de maiz con pollo y verduras",
    "Sopa de platano con carne de res",
    "Sopa de pasta con muslo de pollo",
    "Caldo trifasico con papa criolla",
    "Sopa de zanahoria con costilla ahumada",
    "Sopa de quinua con carne molida"
]

SOPAS_VEGETARIANO = [
    "Sopa de verduras con papa y zanahoria",
    "Crema de ahuyama con semillas tostadas",
    "Sopa de lentejas con apio y cebolla",
    "Crema de brocoli con papa",
    "Sopa de arveja con zanahoria y cilantro",
    "Crema de tomate con albahaca fresca",
    "Sopa de quinua con verduras de temporada",
    "Sopa de pasta con champiñones y espinaca",
    "Crema de papa con cebolla caramelizada",
    "Sopa de fideos con espinaca y ajo",
    "Sopa de cebada con verduras mixtas",
    "Crema de zanahoria con jengibre",
    "Sopa de platano verde con papa y cilantro",
    "Crema de maiz con leche de coco",
    "Sopa de garbanzo con tomate y pimentón",
    "Crema de lenteja roja con curry",
    "Sopa de guineo con papa y cebolla",
    "Crema de espinaca con nuez moscada",
    "Sopa de arroz con verduras y limon",
    "Crema de remolacha con manzana"
]

SECOS_CARNIVORO = [
    "Arroz blanco, pollo sudado con papa y zanahoria",
    "Arroz blanco, bistec de res encebollado con papa al vapor",
    "Arroz blanco, pechuga a la plancha con ensalada mixta",
    "Arroz con pollo, frijoles rojos y tajadas de platano maduro",
    "Arroz blanco, carne molida guisada con papa salada",
    "Arroz amarillo, muslo de pollo asado con ensalada de zanahoria",
    "Arroz blanco, lentejas con cerdo y platano verde cocido",
    "Arroz blanco, higado encebollado con papa y aguacate",
    "Arroz blanco, frijoles con cerdo y chicharron",
    "Arroz blanco, sudado de pollo con yuca y ensalada",
    "Arroz con frijoles, blanquillo frito y tajadas de platano",
    "Arroz blanco, carne asada con papas fritas y ensalada",
    "Arroz blanco, pollo al horno con papa salada y aguacate",
    "Arroz blanco, estofado de res con zanahoria y arveja",
    "Arroz blanco, bandeja con frijoles, carne, chicharron y tajadas",
    "Arroz blanco, pollo en salsa criolla con papa al vapor",
    "Arroz blanco, chuleta de cerdo a la plancha con ensalada",
    "Arroz con arveja, pechuga desmechada con papa salada",
    "Arroz blanco, carne en salsa de tomate con yuca frita",
    "Arroz blanco, pollo apanado con papas fritas y limon",
    "Arroz blanco, lomo de cerdo con frijoles y tajadas",
    "Arroz blanco, carne mechada con papa y ensalada de repollo",
    "Arroz blanco, pollo con champiñones y papa al vapor",
    "Arroz amarillo, res en salsa negra con papa criolla"
]

SECOS_VEGETARIANO = [
    "Arroz blanco, lentejas guisadas con zanahoria y ensalada verde",
    "Arroz blanco, frijoles rojos con platano maduro y aguacate",
    "Arroz integral, tofu salteado con verduras y papa al vapor",
    "Arroz blanco, garbanzo guisado con espinaca y ensalada mixta",
    "Arroz blanco, tortilla de huevo con papa salada y ensalada",
    "Arroz amarillo, arveja guisada con zanahoria y tajadas",
    "Arroz blanco, berenjena gratinada con papa al vapor",
    "Arroz blanco, frijoles negros con platano verde y ensalada",
    "Arroz blanco, revuelto de huevo con champiñones y papa",
    "Arroz blanco, lentejas al curry con papa y ensalada",
    "Arroz blanco, blanquillo con papas fritas y ensalada",
    "Arroz con frijoles, tajadas de platano y ensalada de zanahoria",
    "Arroz blanco, torta de papa con ensalada mixta",
    "Arroz blanco, garbanzos con espinaca y aguacate",
    "Arroz blanco, guiso de verduras con papa y mazorca",
    "Arroz integral, quinua con verduras salteadas y aguacate",
    "Arroz blanco, frijoles blancos con espinaca y papa al vapor",
    "Arroz blanco, hamburguesa de lenteja con papas fritas",
    "Arroz blanco, arveja con zanahoria y huevo duro",
    "Arroz blanco, tofu en salsa de tomate con papa salada",
    "Arroz amarillo, champiñones salteados con papa criolla",
    "Arroz blanco, torta de zanahoria con frijoles y tajadas",
    "Arroz con espinaca, huevo al gusto y ensalada de pepino",
    "Arroz blanco, cazuela de verduras con mazorca y aguacate",
    "Arroz blanco, lentejas con platano maduro y ensalada fresca"
]

INFO_CARNIVORO = [
    {"calorias": "620 kcal", "proteinas": "30g", "carbohidratos": "70g", "grasas": "16g"},
    {"calorias": "635 kcal", "proteinas": "31g", "carbohidratos": "71g", "grasas": "17g"},
    {"calorias": "650 kcal", "proteinas": "32g", "carbohidratos": "75g", "grasas": "18g"},
    {"calorias": "660 kcal", "proteinas": "33g", "carbohidratos": "74g", "grasas": "19g"},
    {"calorias": "670 kcal", "proteinas": "34g", "carbohidratos": "73g", "grasas": "19g"},
    {"calorias": "680 kcal", "proteinas": "35g", "carbohidratos": "72g", "grasas": "20g"},
    {"calorias": "690 kcal", "proteinas": "36g", "carbohidratos": "71g", "grasas": "21g"},
    {"calorias": "700 kcal", "proteinas": "38g", "carbohidratos": "68g", "grasas": "22g"},
    {"calorias": "710 kcal", "proteinas": "39g", "carbohidratos": "70g", "grasas": "22g"},
    {"calorias": "720 kcal", "proteinas": "40g", "carbohidratos": "71g", "grasas": "24g"},
    {"calorias": "730 kcal", "proteinas": "41g", "carbohidratos": "69g", "grasas": "25g"},
    {"calorias": "745 kcal", "proteinas": "42g", "carbohidratos": "67g", "grasas": "26g"}
]

INFO_VEGETARIANO = [
    {"calorias": "480 kcal", "proteinas": "17g", "carbohidratos": "72g", "grasas": "9g"},
    {"calorias": "495 kcal", "proteinas": "18g", "carbohidratos": "73g", "grasas": "9g"},
    {"calorias": "510 kcal", "proteinas": "19g", "carbohidratos": "75g", "grasas": "10g"},
    {"calorias": "520 kcal", "proteinas": "20g", "carbohidratos": "76g", "grasas": "11g"},
    {"calorias": "530 kcal", "proteinas": "21g", "carbohidratos": "77g", "grasas": "11g"},
    {"calorias": "540 kcal", "proteinas": "22g", "carbohidratos": "78g", "grasas": "12g"},
    {"calorias": "555 kcal", "proteinas": "23g", "carbohidratos": "79g", "grasas": "12g"},
    {"calorias": "565 kcal", "proteinas": "24g", "carbohidratos": "80g", "grasas": "13g"},
    {"calorias": "575 kcal", "proteinas": "25g", "carbohidratos": "81g", "grasas": "13g"},
    {"calorias": "585 kcal", "proteinas": "26g", "carbohidratos": "82g", "grasas": "14g"},
    {"calorias": "595 kcal", "proteinas": "27g", "carbohidratos": "83g", "grasas": "14g"},
    {"calorias": "610 kcal", "proteinas": "28g", "carbohidratos": "84g", "grasas": "15g"}
]

INGREDIENTES_CARNIVORO = [
    ["arroz", "pollo", "papa", "zanahoria", "cebolla", "tomate"],
    ["arroz", "carne de res", "papa", "cebolla", "pimentón", "ajo"],
    ["arroz", "cerdo", "frijoles", "platano", "chicharron"],
    ["arroz", "pollo", "yuca", "mazorca", "cebolla", "cilantro"],
    ["arroz", "higado de res", "papa", "cebolla", "aguacate"],
    ["arroz", "carne molida", "arveja", "zanahoria", "papa"],
    ["arroz", "gallina", "papa", "mazorca", "guascas", "cilantro"],
    ["arroz", "costilla de res", "papa", "yuca", "cilantro"],
    ["arroz", "pechuga", "champiñones", "papa", "ajo"],
    ["arroz", "lomo de cerdo", "frijoles", "platano", "cebolla"],
    ["arroz", "carne asada", "papa", "ensalada", "tomate"],
    ["arroz", "chuleta de cerdo", "papa criolla", "cebolla", "ajo"]
]

INGREDIENTES_VEGETARIANO = [
    ["arroz", "lentejas", "zanahoria", "cebolla", "ajo", "tomate"],
    ["arroz", "frijoles", "platano", "cebolla", "aguacate"],
    ["arroz", "garbanzo", "espinaca", "ajo", "cebolla", "limon"],
    ["arroz", "huevo", "champiñones", "cebolla", "papa"],
    ["arroz", "tofu", "brocoli", "zanahoria", "soya", "ajo"],
    ["arroz", "arveja", "zanahoria", "papa", "cebolla"],
    ["arroz", "berenjena", "papa", "ajo", "tomate", "pimentón"],
    ["arroz", "quinua", "verduras mixtas", "cebolla", "ajo"],
    ["arroz", "frijoles negros", "platano verde", "ajo", "cebolla"],
    ["arroz", "lentejas rojas", "curry", "papa", "leche de coco"],
    ["arroz", "champiñones", "papa criolla", "ajo", "tomillo"],
    ["arroz", "espinaca", "huevo", "pepino", "cebolla", "limon"]
]

ALERGIAS_CARNIVORO   = [["gluten"], [], ["lactosa"], ["gluten", "lactosa"], [], [], [], []]
ALERGIAS_VEGETARIANO = [["huevo"], [], ["soya"], ["gluten"], [], ["lactosa"], [], []]

FECHA_INICIO = date(2020, 1, 1)
FECHA_FIN    = date(2026, 6, 30)
BATCH_SIZE   = 500


def generar_fechas_habiles(inicio, fin):
    """Genera fechas habiles (lunes-viernes, sin festivos) como datetime."""
    fechas = []
    actual = inicio
    while actual <= fin:
        if actual.weekday() < 5 and actual not in FESTIVOS:
            fechas.append(datetime(actual.year, actual.month, actual.day))
        actual += timedelta(days=1)
    return fechas


def insertar_menus():
    db    = obtener_bd()
    col   = db[Menu.coleccion]
    sedes = list(db[Sede.coleccion].find({}, {
        "_id": 1,
        "nombre_sede": 1,
        "ubicacion": 1
    }))

    if not sedes:
        print("ERROR: No hay sedes. Ejecuta insertar_sedes.py primero.")
        return

    col.delete_many({})
    print("Coleccion Menus_Diarios limpiada.")

    fechas    = generar_fechas_habiles(FECHA_INICIO, FECHA_FIN)
    total_est = len(fechas) * len(sedes) * 2
    print(f"Fechas habiles (sin festivos): {len(fechas)}")
    print(f"Sedes                        : {len(sedes)}")
    print(f"Total estimado               : {total_est:,} menus\n")

    batch      = []
    insertados = 0

    for fecha in fechas:
        for sede in sedes:

            sopa_c = random.choice(SOPAS_CARNIVORO)
            seco_c = random.choice(SECOS_CARNIVORO)
            sopa_v = random.choice(SOPAS_VEGETARIANO)
            seco_v = random.choice(SECOS_VEGETARIANO)

            # sede_id como objeto embebido SOLO con nombre y ubicacion
            # (sin el ObjectId real de la sede)
            embed_sede = {
                "nombre_sede": sede["nombre_sede"],
                "ubicacion":   sede.get("ubicacion", "")
            }

            menu_c = Menu(
                sede_id              = embed_sede,
                fecha                = fecha,
                tipo_comida          = "carnivoro",
                plato                = f"{sopa_c} / {seco_c}",
                info_nutricional     = random.choice(INFO_CARNIVORO),
                ingredientes         = random.choice(INGREDIENTES_CARNIVORO),
                advertencia_alergias = random.choice(ALERGIAS_CARNIVORO)
            )

            menu_v = Menu(
                sede_id              = embed_sede,
                fecha                = fecha,
                tipo_comida          = "vegetariano",
                plato                = f"{sopa_v} / {seco_v}",
                info_nutricional     = random.choice(INFO_VEGETARIANO),
                ingredientes         = random.choice(INGREDIENTES_VEGETARIANO),
                advertencia_alergias = random.choice(ALERGIAS_VEGETARIANO)
            )

            batch.append(menu_c.to_dict())
            batch.append(menu_v.to_dict())

            if len(batch) >= BATCH_SIZE:
                col.insert_many(batch)
                insertados += len(batch)
                pct = round(insertados / total_est * 100, 1)
                print(f"  Insertados: {insertados:,}/{total_est:,} ({pct}%)")
                batch = []

    if batch:
        col.insert_many(batch)
        insertados += len(batch)

    print(f"\nMenus insertados: {insertados:,}")


if __name__ == "__main__":
    insertar_menus()