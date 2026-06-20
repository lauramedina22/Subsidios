"""
conexion.py
Módulo de conexión a MongoDB. Reutilizable tanto en scripts de setup
como en la app de Streamlit.
"""

import os
from pathlib import Path
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
NOMBRE_BD = os.getenv("NOMBRE_BD", "comedor_universitario")


@st.cache_resource
def obtener_cliente():
    """Crea el MongoClient una sola vez y lo reutiliza entre reruns."""
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    cliente.admin.command("ping")
    return cliente


def obtener_bd():
    """Devuelve la referencia a la base de datos usando el cliente cacheado."""
    return obtener_cliente()[NOMBRE_BD]


if __name__ == "__main__":
    db = obtener_bd()
    print("Conectado a:", db.name)
    print("Colecciones existentes:", db.list_collection_names())
   