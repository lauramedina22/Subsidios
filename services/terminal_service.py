"""
terminal_service.py
Parser de sintaxis MongoDB shell → PyMongo.
Soporta:
  - Sintaxis JS: claves sin comillas, true/false/null, ISODate/Date/string para fechas
  - Comandos: find, findOne, countDocuments, distinct, aggregate, insertOne,
              insertMany, updateOne, updateMany, deleteOne, deleteMany
  - Encadenados: .sort().limit().skip()
  - Pipeline: $match $project $group $sort $limit $skip $unwind $lookup $count
  - Operadores: $eq $gt $gte $lt $lte $ne $and $or $not $in $nin
               $sum $avg $min $max $first $last $push $concat $size $arrayElemAt
"""

import re
import json
from datetime import datetime
from bson import ObjectId
from connection import obtener_bd

MAX_RESULTADOS = 500   # Se traen hasta 500; la paginación del UI muestra de a 25

# ──────────────────────────────────────────────
# UTILIDADES DE SERIALIZACIÓN
# ──────────────────────────────────────────────

def _serializar(valor):
    if isinstance(valor, dict):
        return {k: _serializar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_serializar(i) for i in valor]
    if isinstance(valor, ObjectId):
        return str(valor)
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")
    return valor


# ──────────────────────────────────────────────
# PARSER JS → PYTHON
# ──────────────────────────────────────────────

# Detectar qué sintaxis de fecha usó el usuario
DATE_PATTERNS = {
    "ISODate": re.compile(r'ISODate\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    "Date":    re.compile(r'\bDate\s*\(\s*["\']([^"\']+)["\']\s*\)'),
}

def _detectar_sintaxis_fecha(texto: str) -> str | None:
    """Retorna 'ISODate', 'Date', 'string' o None si no hay fechas."""
    for nombre, pat in DATE_PATTERNS.items():
        if pat.search(texto):
            return nombre
    # Buscar strings que parezcan fechas ISO dentro del texto
    if re.search(r'"\d{4}-\d{2}-\d{2}"', texto) or re.search(r"'\d{4}-\d{2}-\d{2}'", texto):
        return "string"
    return None


def _normalizar_js(texto: str) -> str:
    """
    Convierte texto estilo MongoDB shell a JSON válido que Python puede parsear.
    Pasos:
      1. ISODate("...") / Date("...") / "YYYY-MM-DD" → "__DATE__YYYY-MM-DD__"
      2. ObjectId("...") → "__OID__....__"
      3. true/false/null → True/False/None (marcadores temporales)
      4. Claves sin comillas → con comillas
      5. Comillas simples → dobles
      6. Trailing commas
    """
    # 1a. ISODate("...") → placeholder
    texto = re.sub(
        r'ISODate\s*\(\s*["\']([^"\']+)["\']\s*\)',
        r'"__DATE__\1__"',
        texto
    )
    # 1b. Date("...") → placeholder
    texto = re.sub(
        r'\bDate\s*\(\s*["\']([^"\']+)["\']\s*\)',
        r'"__DATE__\1__"',
        texto
    )
    # 1c. Strings que parecen fecha ISO sola (no dentro de otra cosa)
    # No tocamos, se manejan al parsear el valor string

    # 2. ObjectId("...") → placeholder
    texto = re.sub(
        r'ObjectId\s*\(\s*["\']([^"\']+)["\']\s*\)',
        r'"__OID__\1__"',
        texto
    )

    # 3. Booleanos y null JS → marcadores que JSON entiende
    texto = re.sub(r'\btrue\b',  'true',  texto)
    texto = re.sub(r'\bfalse\b', 'false', texto)
    texto = re.sub(r'\bnull\b',  'null',  texto)

    # 4. Claves sin comillas: {campo: ...} → {"campo": ...}
    #    Incluye claves con $ como $match, $group, etc.
    #    Capturamos el delimitador como grupo para evitar lookbehind de ancho variable.
    texto = re.sub(
        r'([\{\[,])\s*(\$?[a-zA-Z_][a-zA-Z0-9_\.]*)\s*:',
        lambda m: m.group(1) + ' "' + m.group(2) + '":',
        texto
    )
    # Segunda pasada: claves al inicio de línea / tras newline
    texto = re.sub(
        r'(^\s*|\n\s*)(\$?[a-zA-Z_][a-zA-Z0-9_\.]*)\s*:',
        lambda m: m.group(1) + '"' + m.group(2) + '":',
        texto
    )

    # 5. Comillas simples → dobles (fuera de strings ya entre comillas dobles)
    texto = re.sub(r"(?<!\\)'", '"', texto)

    # 6. Trailing commas antes de } o ]
    texto = re.sub(r',\s*([\}\]])', r'\1', texto)

    return texto


def _parsear_valor(texto_normalizado: str):
    """
    Parsea texto JSON normalizado a objeto Python.
    Después reemplaza los placeholders de fecha y ObjectId.
    """
    try:
        obj = json.loads(texto_normalizado)
    except json.JSONDecodeError as e:
        raise ValueError(f"No se pudo parsear el argumento: {e}\nTexto: {texto_normalizado}")
    return _resolver_placeholders(obj)


def _resolver_placeholders(obj):
    """Recorre recursivamente y convierte __DATE__ y __OID__ a tipos reales."""
    if isinstance(obj, dict):
        return {k: _resolver_placeholders(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolver_placeholders(i) for i in obj]
    if isinstance(obj, str):
        if obj.startswith("__DATE__") and obj.endswith("__"):
            fecha_str = obj[8:-2]
            try:
                return datetime.fromisoformat(fecha_str)
            except ValueError:
                return datetime.strptime(fecha_str, "%Y-%m-%d")
        if obj.startswith("__OID__") and obj.endswith("__"):
            oid_str = obj[7:-2]
            return ObjectId(oid_str)
        # String que parece fecha ISO directa
        if re.match(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?)?$', obj):
            try:
                return datetime.fromisoformat(obj)
            except ValueError:
                pass
    return obj


# ──────────────────────────────────────────────
# EXTRACTOR DE ARGUMENTOS
# ──────────────────────────────────────────────

def _extraer_args(texto_args: str) -> list:
    """
    Divide el texto de argumentos respetando anidamiento de {} y [].
    Retorna lista de strings, uno por argumento.
    """
    args = []
    nivel = 0
    inicio = 0
    en_string = False
    char_string = None

    for i, ch in enumerate(texto_args):
        if en_string:
            if ch == char_string and (i == 0 or texto_args[i-1] != '\\'):
                en_string = False
        else:
            if ch in ('"', "'"):
                en_string = True
                char_string = ch
            elif ch in ('{', '[', '('):
                nivel += 1
            elif ch in ('}', ']', ')'):
                nivel -= 1
            elif ch == ',' and nivel == 0:
                seg = texto_args[inicio:i].strip()
                if seg:
                    args.append(seg)
                inicio = i + 1

    seg = texto_args[inicio:].strip()
    if seg:
        args.append(seg)

    return args


# ──────────────────────────────────────────────
# PARSER PRINCIPAL DE COMANDO
# ──────────────────────────────────────────────

# Regex para capturar: db.coleccion.metodo(args)
CMD_RE = re.compile(
    r'^db\s*\.\s*(\w+)\s*\.\s*(\w+)\s*\(([\s\S]*)\)\s*$',
    re.DOTALL
)

# Encadenados: .sort({}) .limit(N) .skip(N)
CHAIN_RE = re.compile(
    r'\.\s*(sort|limit|skip)\s*\(([^)]*)\)',
    re.DOTALL
)


def _parsear_comando(consulta: str) -> dict:
    """
    Retorna:
      {
        coleccion: str,
        metodo: str,
        args: list,
        encadenados: list[{metodo, arg}],
        sintaxis_fecha: str | None,
      }
    """
    consulta = consulta.strip().rstrip(';')

    # Extraer encadenados al final: .sort(...).limit(...)
    encadenados = []
    def _capturar_chain(m):
        encadenados.append({"metodo": m.group(1), "arg": m.group(2).strip()})
        return ""

    # Separar la parte base de los encadenados
    # Los encadenados van DESPUÉS del cierre del paréntesis principal
    # Estrategia: encontrar el último ')' del método principal
    base = consulta
    sufijo = ""

    # Buscar el paréntesis de cierre del método principal
    nivel = 0
    pos_apertura = None
    pos_cierre = None
    for i, ch in enumerate(consulta):
        if ch == '(' and pos_apertura is None:
            # Verificar que sea la apertura del método
            antes = consulta[:i].rstrip()
            if re.search(r'db\s*\.\s*\w+\s*\.\s*\w+$', antes):
                pos_apertura = i
                nivel = 1
        elif pos_apertura is not None:
            if ch == '(':
                nivel += 1
            elif ch == ')':
                nivel -= 1
                if nivel == 0:
                    pos_cierre = i
                    break

    if pos_cierre is not None:
        base   = consulta[:pos_cierre+1]
        sufijo = consulta[pos_cierre+1:]

    # Parsear encadenados del sufijo
    for m in CHAIN_RE.finditer(sufijo):
        encadenados.append({"metodo": m.group(1), "arg": m.group(2).strip()})

    # Detectar sintaxis de fecha en el texto original
    sintaxis_fecha = _detectar_sintaxis_fecha(consulta)

    # Parsear base: db.coleccion.metodo(args)
    m = CMD_RE.match(base)
    if not m:
        raise ValueError(
            "Sintaxis no reconocida. Formato esperado:\n"
            "  db.coleccion.metodo({filtro})\n"
            "  db.coleccion.aggregate([...])"
        )

    coleccion = m.group(1)
    metodo    = m.group(2)
    args_raw  = m.group(3).strip()

    # Parsear argumentos
    args_parsed = []
    if args_raw:
        partes = _extraer_args(args_raw)
        for parte in partes:
            normalizado = _normalizar_js(parte)
            args_parsed.append(_parsear_valor(normalizado))

    return {
        "coleccion":     coleccion,
        "metodo":        metodo,
        "args":          args_parsed,
        "encadenados":   encadenados,
        "sintaxis_fecha": sintaxis_fecha,
    }


# ──────────────────────────────────────────────
# EJECUTOR
# ──────────────────────────────────────────────

METODOS_LECTURA  = {"find", "findOne", "countDocuments", "distinct", "aggregate"}
METODOS_ESCRITURA = {"insertOne", "insertMany", "updateOne", "updateMany", "deleteOne", "deleteMany"}
METODOS_VALIDOS  = METODOS_LECTURA | METODOS_ESCRITURA


def _aplicar_encadenados(cursor, encadenados: list):
    for enc in encadenados:
        metodo = enc["metodo"]
        arg_raw = enc["arg"]
        if metodo == "sort":
            arg = _parsear_valor(_normalizar_js(arg_raw))
            if isinstance(arg, dict):
                cursor = cursor.sort(list(arg.items()))
            else:
                cursor = cursor.sort(arg)
        elif metodo == "limit":
            cursor = cursor.limit(int(arg_raw))
        elif metodo == "skip":
            cursor = cursor.skip(int(arg_raw))
    return cursor


def _cursor_a_lista(cursor, max_res=MAX_RESULTADOS):
    docs = []
    truncado = False
    for i, doc in enumerate(cursor):
        if i >= max_res:
            truncado = True
            break
        docs.append(_serializar(doc))
    return docs, truncado


class TerminalService:
    def __init__(self):
        self.db = obtener_bd()

    def ejecutar(self, consulta: str) -> dict:
        consulta = consulta.strip()
        if not consulta:
            return {"tipo": "error", "mensaje": "La consulta está vacía."}

        try:
            cmd = _parsear_comando(consulta)
        except ValueError as e:
            return {"tipo": "error", "mensaje": str(e)}

        coleccion    = cmd["coleccion"]
        metodo       = cmd["metodo"]
        args         = cmd["args"]
        encadenados  = cmd["encadenados"]
        sintaxis_fecha = cmd["sintaxis_fecha"]

        if metodo not in METODOS_VALIDOS:
            return {
                "tipo": "error",
                "mensaje": (
                    f"Método '{metodo}' no soportado.\n"
                    f"Métodos disponibles: {', '.join(sorted(METODOS_VALIDOS))}"
                )
            }

        col = self.db[coleccion]

        try:
            # ── LECTURA ──
            if metodo == "find":
                filtro     = args[0] if len(args) > 0 else {}
                proyeccion = args[1] if len(args) > 1 else None
                cursor = col.find(filtro, proyeccion) if proyeccion else col.find(filtro)
                cursor = _aplicar_encadenados(cursor, encadenados)
                docs, truncado = _cursor_a_lista(cursor)
                # total_bd: cuántos hay realmente en BD (para mostrar en cabecera)
                tiene_limit = any(e["metodo"] == "limit" for e in encadenados)
                total_bd = col.count_documents(filtro) if not tiene_limit else len(docs)
                return {
                    "tipo": "tabla", "datos": docs,
                    "truncado": truncado, "total": len(docs),
                    "total_bd": total_bd,
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "findOne":
                filtro     = args[0] if len(args) > 0 else {}
                proyeccion = args[1] if len(args) > 1 else None
                doc = col.find_one(filtro, proyeccion) if proyeccion else col.find_one(filtro)
                if doc is None:
                    return {
                        "tipo": "escalar", "valor": None,
                        "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                    }
                return {
                    "tipo": "tabla", "datos": [_serializar(doc)],
                    "truncado": False, "total": 1,
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "countDocuments":
                filtro = args[0] if len(args) > 0 else {}
                n = col.count_documents(filtro)
                return {
                    "tipo": "escalar", "valor": n,
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "distinct":
                campo  = args[0] if len(args) > 0 else ""
                filtro = args[1] if len(args) > 1 else {}
                vals = col.distinct(campo, filtro)
                return {
                    "tipo": "lista", "datos": [_serializar(v) for v in vals],
                    "total": len(vals), "metodo": metodo,
                    "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "aggregate":
                pipeline = args[0] if len(args) > 0 else []
                cursor = col.aggregate(pipeline)
                docs, truncado = _cursor_a_lista(cursor)
                return {
                    "tipo": "tabla", "datos": docs,
                    "truncado": truncado, "total": len(docs),
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            # ── ESCRITURA ──
            elif metodo == "insertOne":
                doc = args[0] if len(args) > 0 else {}
                res = col.insert_one(doc)
                return {
                    "tipo": "escalar",
                    "valor": f"Documento insertado. _id: {res.inserted_id}",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "insertMany":
                docs = args[0] if len(args) > 0 else []
                res = col.insert_many(docs)
                return {
                    "tipo": "escalar",
                    "valor": f"{len(res.inserted_ids)} documentos insertados.",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "updateOne":
                filtro = args[0] if len(args) > 0 else {}
                update = args[1] if len(args) > 1 else {}
                res = col.update_one(filtro, update)
                return {
                    "tipo": "escalar",
                    "valor": f"Encontrados: {res.matched_count} | Modificados: {res.modified_count}",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "updateMany":
                filtro = args[0] if len(args) > 0 else {}
                update = args[1] if len(args) > 1 else {}
                res = col.update_many(filtro, update)
                return {
                    "tipo": "escalar",
                    "valor": f"Encontrados: {res.matched_count} | Modificados: {res.modified_count}",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "deleteOne":
                filtro = args[0] if len(args) > 0 else {}
                res = col.delete_one(filtro)
                return {
                    "tipo": "escalar",
                    "valor": f"Documentos eliminados: {res.deleted_count}",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

            elif metodo == "deleteMany":
                filtro = args[0] if len(args) > 0 else {}
                res = col.delete_many(filtro)
                return {
                    "tipo": "escalar",
                    "valor": f"Documentos eliminados: {res.deleted_count}",
                    "metodo": metodo, "sintaxis_fecha": sintaxis_fecha,
                }

        except Exception as e:
            return {"tipo": "error", "mensaje": f"{type(e).__name__}: {e}"}