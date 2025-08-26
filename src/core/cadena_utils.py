import os
import json

CARGA_PATH = os.path.join("data", "CadenaCharada.json")
cadena_charada = {}

# 🔄 Cargar una vez al iniciar
if os.path.exists(CARGA_PATH):
    with open(CARGA_PATH, "r", encoding="utf-8") as f:
        cadena_charada = json.load(f)
else:
    print("❌ Archivo CadenaCharada.json no encontrado.")

# 🔍 Obtener cadena a partir de un número

def obtener_cadena(numero: str):
    try:
        numero = str(int(numero)).zfill(2)  # Asegura formato "00"
    except:
        return None

    if numero not in cadena_charada:
        return None

    items = cadena_charada[numero]
    if not items:
        return None

    encabezado = items[0]  # Primer elemento es el propio número
    sugerencias = items[1:] if len(items) > 1 else []
    return {
        "base": encabezado,
        "sugerencias": sugerencias
    }
