import os
import json
from datetime import datetime

# 📁 Ruta del JSON generado con predicciones
PREDICCIONES_JSON = "data/predicciones_2025_2026.json"

# 📦 Estructura en memoria
predicciones = []
json_cargado = False

# 🔄 Cargar predicciones desde el archivo JSON
def cargar_json_predicciones():
    global predicciones, json_cargado
    if os.path.exists(PREDICCIONES_JSON):
        with open(PREDICCIONES_JSON, "r", encoding="utf-8") as f:
            predicciones = json.load(f)
        json_cargado = True
        print("✅ Predicciones JSON cargadas.")
    else:
        print("❌ Archivo de predicciones no encontrado.")
        json_cargado = False

# 🔮 Buscar predicciones por fecha, estado y draw
def predecir_fijos_ia(fecha: str, estado: str, draw: str, top_n=5):
    global json_cargado
    if not json_cargado:
        cargar_json_predicciones()
    
    if not json_cargado:
        raise RuntimeError("❌ No se pudo cargar el archivo de predicciones.")

    try:
        fecha_obj = datetime.strptime(fecha, "%d/%m/%y")
        fecha_str = fecha_obj.strftime("%d/%m/%y")  # Coincide con el formato del JSON
    except:
        raise ValueError("❌ Formato de fecha inválido. Usa dd/mm/aa")

    for item in predicciones:
        if item["date"] == fecha_str and item["state"] == estado and item["draw"] == draw:
            top_pred = item["predicciones"][:top_n]
            print("📅", fecha_str, estado, draw)
            print("🔮 Top predicciones:", top_pred)
            return top_pred

    raise ValueError("⚠️ No se encontraron predicciones para esa combinación de fecha, estado y turno.")

