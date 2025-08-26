from collections import defaultdict
from datetime import datetime

TURNOS_ORDEN = {"M": 0, "E": 1, "N": 2}

def calcular_peso(fecha_str):
    anio = int(fecha_str.split("/")[-1])
    anio += 2000 if anio < 50 else 1900
    if anio >= 2023:
        return 3
    elif anio >= 2015:
        return 2
    else:
        return 1

def fijo_base(fijo):
    return min(fijo, fijo[::-1])

def predecir_por_secuencia_estado(sorteos, estado_objetivo, draw_objetivo, valores, tamanio=2, modo="normal"):
    secuencia = [fijo_base(f) for f in valores[-tamanio:]]
    secuencia_invertida = secuencia[::-1]
    ocurrencias = defaultdict(int)
    detalles = defaultdict(list)
    total_pesado = 0

    # Filtrar sorteos del estado
    sorteos_estado = [s for s in sorteos if s["state"] == estado_objetivo and len(s["fijos"]) > 0]

    # Ordenar por fecha y turno
    sorteos_estado.sort(key=lambda s: (datetime.strptime(s["date"], "%d/%m/%y"), TURNOS_ORDEN.get(s["draw"], 9)))

    # Lista de sorteos planos: cada entrada representa 1 sorteo completo
    historico = [
        {
            "fijos": [fijo_base(f) for f in s["fijos"]],
            "fecha": s["date"],
            "draw": s["draw"]
        }
        for s in sorteos_estado
    ]

    for i in range(len(historico) - tamanio):
        match = True
        for j in range(tamanio):
            if secuencia[j] not in historico[i + j]["fijos"]:
                match = False
                break
        if not match:
            match = True
            for j in range(tamanio):
                if secuencia_invertida[j] not in historico[i + j]["fijos"]:
                    match = False
                    break
        if not match:
            continue

        if i + tamanio < len(historico):
            peso = calcular_peso(historico[i + tamanio - 1]["fecha"])
            for fijo in historico[i + tamanio]["fijos"]:
                base = fijo_base(fijo)
                if base in secuencia:
                    continue
                p = peso + 1 if historico[i + tamanio]["draw"] == draw_objetivo else peso
                ocurrencias[base] += p
                detalles[base].append({
                    "fecha": historico[i + tamanio]["fecha"],
                    "draw": historico[i + tamanio]["draw"],
                    "peso": p
                })
                total_pesado += p

        if modo == "invertida" and i > 0:
            peso = calcular_peso(historico[i - 1]["fecha"])
            for fijo in historico[i - 1]["fijos"]:
                base = fijo_base(fijo)
                if base in secuencia:
                    continue
                p = peso + 1 if historico[i - 1]["draw"] == draw_objetivo else peso
                ocurrencias[base] += p
                detalles[base].append({
                    "fecha": historico[i - 1]["fecha"],
                    "draw": historico[i - 1]["draw"],
                    "peso": p
                })
                total_pesado += p

    if not ocurrencias:
        return {"error": "❌ No se encontraron coincidencias para esa secuencia en el historial."}

    predicciones = sorted([
        {
            "fijo": fijo,
            "frecuencia": freq,
            "confianza": round((freq / total_pesado) * 100, 2),
            "detalles": detalles[fijo]
        }
        for fijo, freq in ocurrencias.items()
    ], key=lambda x: x["frecuencia"], reverse=True)
    

    return {
        "estado": estado_objetivo,
        "draw_objetivo": draw_objetivo,
        "modo": modo,
        "tamanio": tamanio,
        "entrada": secuencia,
        "total_observaciones": total_pesado,
        "predicciones": predicciones
    }
