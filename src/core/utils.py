import json
from datetime import datetime
# Orden global fijo con el formato correcto
ORDEN_GLOBAL = [
    "GA_M", "FL_M", "NY_M",
    "GA_E", "FL_E", "NY_E",
    "GA_N"
]
def cargar_sorteos(ruta_json):
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def obtener_loterias_ordenadas(sorteos):
    # Detectar combinaciones válidas en el JSON y devolverlas en orden
    presentes = set(f"{s['state'].upper()}_{s['draw'].upper()}" for s in sorteos)
    ordenadas = [l for l in ORDEN_GLOBAL if l in presentes]
    return ordenadas

def obtener_turno_orden(draw):
    orden = {"M": 0, "E": 1, "N": 2}
    return orden.get(draw, 99)

def filtrar_anteriores(objetivo, posibles):
    if objetivo not in ORDEN_GLOBAL:
        return []
    idx_obj = ORDEN_GLOBAL.index(objetivo)
    return [l for l in ORDEN_GLOBAL[:idx_obj] if l in posibles]


def obtener_historial_ultimo_dia(sorteos):
    if not sorteos:
        return []

    fechas = set(s["date"] for s in sorteos)
    ultima_fecha = max(fechas, key=lambda f: datetime.strptime(f, "%d/%m/%y"))

    # Filtrar sorteos de esa fecha
    sorteos_ultimo_dia = [s for s in sorteos if s["date"] == ultima_fecha]

    # Ordenar según ORDEN_GLOBAL
    def clave_global(s):
        key = f"{s['state'].upper()}_{s['draw'].upper()}"
        return ORDEN_GLOBAL.index(key) if key in ORDEN_GLOBAL else 99

    sorteos_ordenados = sorted(sorteos_ultimo_dia, key=clave_global)

    return ultima_fecha, sorteos_ordenados

def obtener_meses_y_anios(sorteos):
    fechas = set(s["date"] for s in sorteos)
    meses_anios = set()
    for f in fechas:
        dt = datetime.strptime(f, "%d/%m/%y")
        meses_anios.add((dt.year, dt.month))
    return sorted(meses_anios)

def filtrar_por_mes_y_anio(sorteos, anio, mes):
    resultados = []
    for s in sorteos:
        dt = datetime.strptime(s["date"], "%d/%m/%y")
        if dt.year == anio and dt.month == mes:
            resultados.append((dt, s))
    # Orden por fecha y luego orden global
    def clave_orden(x):
        clave = f"{x[1]['state'].upper()}_{x[1]['draw'].upper()}"
        orden_idx = ORDEN_GLOBAL.index(clave) if clave in ORDEN_GLOBAL else 99
        return (x[0], orden_idx)

    return [s for _, s in sorted(resultados, key=clave_orden)]
