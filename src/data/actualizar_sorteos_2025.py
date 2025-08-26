import os
import json
import requests
from datetime import datetime

ARCHIVO_JSON = "data/sorteos_unificados_con_fijos.json"

EMAIL = "khloealba932@gmail.com"
PASSWORD = "Anabelyae04"

URLS_TXT = {
    ("GA", "M"): "https://www.lotterycorner.com/results/download/ga-cash-3-midday-2025.txt",
    ("GA", "E"): "https://www.lotterycorner.com/results/download/ga-cash-3-evening-2025.txt",
    ("GA", "N"): "https://www.lotterycorner.com/results/download/ga-cash-3-night-2025.txt",
    ("FL", "M"): "https://www.lotterycorner.com/results/download/fl-pick-3-midday-2025.txt",
    ("FL", "E"): "https://www.lotterycorner.com/results/download/fl-pick-3-evening-2025.txt",
    ("NY", "M"): "https://www.lotterycorner.com/results/download/ny-numbers-midday-2025.txt",
    ("NY", "E"): "https://www.lotterycorner.com/results/download/ny-numbers-evening-2025.txt",
}

PRIORIDAD = {
    "GA_M": 0, "FL_M": 1, "NY_M": 2,
    "GA_E": 3, "FL_E": 4, "NY_E": 5,
    "GA_N": 6
}

def generar_fijos(numeros):
    partes = numeros.split("-")
    return [partes[1] + partes[2], partes[2] + partes[1]]

def login_y_descargar_archivos(log):
    session = requests.Session()
    login_url = "https://www.lotterycorner.com/insider/login"
    login_data = {
        "email": EMAIL,
        "pwd": PASSWORD
    }
    r = session.post(login_url, data=login_data)
    if "Logout" not in r.text:
        raise Exception("❌ Login fallido. Verifica credenciales.")

    contenidos = {}
    for (estado, sorteo), url in URLS_TXT.items():
        log(f"⬇️ Descargando {estado}_{sorteo}...")
        r = session.get(url)
        r.raise_for_status()
        contenidos[(estado, sorteo)] = r.text
    return contenidos

def parsear_txt(texto, estado, sorteo):
    resultados = []
    lineas = texto.strip().splitlines()[1:]  # Saltar encabezado
    for linea in lineas:
        partes = linea.split(",")
        if len(partes) >= 2:
            fecha_str, numeros = partes[0].strip(), partes[1].strip()
            try:
                fecha = datetime.strptime(fecha_str, "%a %m/%d/%Y")
            except ValueError:
                continue
                
            # Quitar Fire Ball si es FL
            if estado == "FL":
                digitos = numeros.split("-")
                if len(digitos) >= 3:
                    numeros = "-".join(digitos[:3])  # Solo los 3 primeros
                        
            fecha_fmt = fecha.strftime("%d/%m/%y")
            resultados.append({
                "date": fecha_fmt,
                "state": estado,
                "draw": sorteo,
                "numbers": numeros,
                "fijos": generar_fijos(numeros)
            })
    return resultados

def actualizar_sorteos(log):
    combinaciones = {}

    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            existentes = json.load(f)
            for s in existentes:
                clave = f"{s['date']}-{s['state']}-{s['draw']}"
                combinaciones[clave] = s

    log("🔐 Iniciando sesión y descargando archivos...")
    txts = login_y_descargar_archivos(log)

    nuevos_contados = 0
    reemplazos = 0

    for (estado, sorteo), texto in txts.items():
        nuevos = parsear_txt(texto, estado, sorteo)
        for s in nuevos:
            clave = f"{s['date']}-{s['state']}-{s['draw']}"
            if clave in combinaciones:
                if combinaciones[clave]["numbers"] != s["numbers"]:
                    combinaciones[clave] = s
                    reemplazos += 1
            else:
                combinaciones[clave] = s
                nuevos_contados += 1

    todos = list(combinaciones.values())
    todos.sort(key=lambda s: (
        datetime.strptime(s["date"], "%d/%m/%y"),
        PRIORIDAD.get(f'{s["state"]}_{s["draw"]}', 99)
    ))

    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)

    log(f"✅ Nuevos sorteos agregados: {nuevos_contados}")
    log(f"🔁 Reemplazos por actualización: {reemplazos}")
    log(f"📊 Total actual: {len(todos)}")
