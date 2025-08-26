from collections import defaultdict
from datetime import datetime

# Orden lógico de sorteos en el día
ORDEN_TURNOS = {"M": 0, "E": 1, "N": 2}

# Función para predecir fijos según los sorteos anteriores del mismo día
def predecir_fijos(fecha_str, estado_objetivo, turno_objetivo, sorteos):
    fecha_objetivo = datetime.strptime(fecha_str, "%d/%m/%y")
    turno_actual = ORDEN_TURNOS.get(turno_objetivo, 9)

    # 1. Buscar los fijos del mismo día que ocurrieron antes
    fijos_previos = []
    for sorteo in sorteos:
        fecha = datetime.strptime(sorteo["date"], "%d/%m/%y")
        if fecha == fecha_objetivo:
            turno_sorteo = ORDEN_TURNOS.get(sorteo["draw"], 9)
            if turno_sorteo < turno_actual:
                fijos_previos.extend(sorteo["fijos"])

    if not fijos_previos:
        return {"error": "No hay fijos anteriores para ese sorteo."}

    # 2. Buscar en el historial cuántas veces estos fijos fueron seguidos por otros
    transiciones = defaultdict(int)

    for i in range(len(sorteos) - 1):
        actual = sorteos[i]
        siguiente = sorteos[i + 1]

        if any(fijo in actual["fijos"] for fijo in fijos_previos):
            for fijo_sig in siguiente["fijos"]:
                transiciones[fijo_sig] += 1

    # 3. Ordenar por frecuencia
    predicciones = sorted(
        [{"fijo": fijo, "frecuencia": freq} for fijo, freq in transiciones.items()],
        key=lambda x: x["frecuencia"],
        reverse=True
    )

    return {
        "sorteo_objetivo": f"{estado_objetivo}_{turno_objetivo}_{fecha_str}",
        "fijos_previos": list(set(fijos_previos)),
        "fijos_sugeridos": predicciones[:5]
    }
