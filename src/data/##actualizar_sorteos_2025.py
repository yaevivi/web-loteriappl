import os
import json
import requests
from datetime import datetime

ARCHIVO_JSON = "data/sorteos_unificados_con_fijos.json"

PRIORIDAD = {
    "GA_M": 0, "FL_M": 1, "NY_M": 2,
    "GA_E": 3, "FL_E": 4, "NY_E": 5,
    "GA_N": 6
}

def obtener_ultima_entrada():
    if not os.path.exists(ARCHIVO_JSON):
        return None
    with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
        datos = json.load(f)
        if not datos:
            return None
        return datos[-1]  # última entrada del archivo

def solicitar_nuevos_sorteos(ultima):
    url = "https://api-sorteos-loteria.onrender.com/actualizar"
    r = requests.post(url, json=ultima)
    r.raise_for_status()
    return r.json().get("nuevos", [])

def actualizar_sorteos(log):
    combinaciones = {}

    # Cargar existentes
    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            existentes = json.load(f)
            for s in existentes:
                clave = f"{s['date']}-{s['state']}-{s['draw']}"
                combinaciones[clave] = s
    else:
        existentes = []

    #log("📦 Buscando última entrada del archivo...")
    #ultima = obtener_ultima_entrada()
    
    ultima = {
        "date": "31/12/24",
        "state": "GA",
        "draw": "N",
        "numbers": "6-4-2",
        "fijos": [
          "42",
          "24"
        ]
      }    
    if not ultima:
        log("⚠️ No se encontró una entrada válida en el archivo local.")
        return

    log(f"📤 Solicitando datos al API desde: {ultima['date']}--{ultima['state']}--{ultima['draw']}")
    try:
        nuevos = solicitar_nuevos_sorteos(ultima)
    except Exception as e:
        log(f"❌ Error solicitando al API: {e}")
        return

    nuevos_contados = 0
    reemplazos = 0

    for s in nuevos:
        clave = f"{s['date']}-{s['state']}-{s['draw']}"
        if clave in combinaciones:
            if combinaciones[clave]["numbers"] != s["numbers"]:
                combinaciones[clave] = s
                reemplazos += 1
        else:
            combinaciones[clave] = s
            nuevos_contados += 1

    def prioridad(s):
        clave = f"{s['state']}_{s['draw']}"
        return PRIORIDAD.get(clave, 99)

    todos = list(combinaciones.values())
    todos.sort(key=lambda s: (
        datetime.strptime(s["date"], "%d/%m/%y"),
        prioridad(s)
    ))

    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)

    log(f"✅ Nuevos sorteos agregados: {nuevos_contados}")
    log(f"🔁 Reemplazos por actualización: {reemplazos}")
    log(f"📊 Total actual: {len(todos)}")
