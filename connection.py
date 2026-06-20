"""
conexion.py
Módulo de conexión a MongoDB. Reutilizable tanto en scripts de setup
como en la app de Streamlit.
"""

from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
NOMBRE_BD = os.getenv("NOMBRE_BD", "comedor_universitario")


def obtener_bd():
    """Devuelve la referencia a la base de datos."""
    cliente = MongoClient(MONGO_URI)
    return cliente[NOMBRE_BD]


if __name__ == "__main__":
    db = obtener_bd()
    print("Conectado a:", db.name)
    print("Colecciones existentes:", db.list_collection_names())