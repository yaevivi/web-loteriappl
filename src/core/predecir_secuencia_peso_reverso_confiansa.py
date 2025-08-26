from collections import defaultdict
from datetime import datetime

TURNOS_ORDEN = {"M": 0, "E": 1, "N": 2}

def sort_sorteos(sorteos):
    return sorted(
        sorteos,
        key=lambda s: (
            datetime.strptime(s["date"], "%d/%m/%y"),
            TURNOS_ORDEN.get(s["draw"], 9)
        )
    )

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

def predecir_por_secuencia_confianza(sorteos, anteriores, valores_anteriores, objetivo):
    secuencias = defaultdict(lambda: defaultdict(int))
    sorteos_ordenados = sort_sorteos(sorteos)

    por_fecha = defaultdict(list)
    for s in sorteos_ordenados:
        por_fecha[s["date"]].append(s)

    for fecha, sorteos_dia in por_fecha.items():
        mapa_dia = {f"{s['state']}_{s['draw']}": s for s in sorteos_dia}
        if all(k in mapa_dia for k in anteriores + [objetivo]):
            entradas = []
            for clave in anteriores:
                entradas.append(mapa_dia[clave]["fijos"])

            combinaciones = [[]]
            for grupo in entradas:
                combinaciones = [prev + [f] for prev in combinaciones for f in grupo]

            fijos_objetivo = mapa_dia[objetivo]["fijos"]
            peso = calcular_peso(fecha)

            for combinacion in combinaciones:
                clave = tuple(combinacion)
                for fijo_obj in fijos_objetivo:
                    fijo_canonico = fijo_base(fijo_obj)
                    secuencias[clave][fijo_canonico] += peso

    entrada_usuario = tuple(valores_anteriores)
    if entrada_usuario not in secuencias:
        return {"error": f"No hay datos históricos para la entrada {entrada_usuario}."}

    total = sum(secuencias[entrada_usuario].values())

    predicciones = sorted(
        [{
            "fijo": fijo,
            "frecuencia": freq,
            "confianza": round((freq / total) * 100, 2)
        } for fijo, freq in secuencias[entrada_usuario].items()],
        key=lambda x: x["frecuencia"],
        reverse=True
    )

    return {
        "objetivo": objetivo,
        "entrada": entrada_usuario,
        "total_observaciones": total,
        "predicciones": predicciones
    }
