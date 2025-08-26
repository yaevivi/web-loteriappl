import os
import json
from datetime import datetime

# Diccionario de colores por dígito
COLOR_MAP = {
    '0': 'amarillo', '5': 'amarillo',
    '1': 'morado',   '6': 'morado',
    '2': 'verde',    '7': 'verde',
    '3': 'rojo',     '8': 'rojo',
    '4': 'azul',     '9': 'azul'
}

# Orden real de turnos para orden cronológico
ORDEN_DRAW = {"M": 0, "E": 1, "N": 2}

# Cargar datos JSON de sorteos
def cargar_sorteos_json(path="data/sorteos_unificados_con_fijos.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Extraer la secuencia global de colores (orden cronológico)
def extraer_secuencia_colores(data, tipo):
    secuencias_colores = []
    for item in data:
        if tipo == "fijos":
            digitos = item["fijos"][0]
        else:
            digitos = item["numbers"].replace("-", "")
        colores = [COLOR_MAP[d] for d in digitos if d in COLOR_MAP]
        secuencias_colores.append(colores)
    return secuencias_colores

# Predicción por secuencia exacta ingresada
def predecir_por_secuencia_colores(
    secuencia_usuario,
    tipo="numbers",
    tam=3,
    modo="normal",
    estados=None,
    horarios=None,
    desde=None,
    hasta=None
):
    data = cargar_sorteos_json()
    estados = estados or ["FL", "GA", "NY"]
    horarios = horarios or ["M", "E", "N"]
    desde_obj = datetime.strptime(desde, "%d/%m/%y") if desde else None
    hasta_obj = datetime.strptime(hasta, "%d/%m/%y") if hasta else None

    # Filtrar por estado, draw y fecha
    data_filtrada = []
    for item in data:
        try:
            fecha_obj = datetime.strptime(item["date"], "%d/%m/%y")
            if desde_obj and fecha_obj < desde_obj:
                continue
            if hasta_obj and fecha_obj > hasta_obj:
                continue
            if item["state"] not in estados:
                continue
            if item["draw"] not in horarios:
                continue
            data_filtrada.append(item)
        except:
            continue

    # Ordenar por fecha y orden real de draw
    data_filtrada.sort(key=lambda x: (
        datetime.strptime(x["date"], "%d/%m/%y"),
        ORDEN_DRAW.get(x["draw"], 3)
    ))

    secuencia_global = extraer_secuencia_colores(data_filtrada, tipo)
    secuencia_usuario = list(secuencia_usuario)

    resultados = {}
    salto = 2 if tipo == "fijos" else 3

    if modo == "normal":
        for i in range(len(secuencia_global) - 1 - salto):
            plano = sum(secuencia_global[i:i+1+salto], [])
            for j in range(len(plano) - tam - salto + 1):
                if plano[j:j+tam] == secuencia_usuario:
                    siguientes = plano[j+tam:j+tam+salto]
                    if len(siguientes) == salto:
                        clave = tuple(siguientes)
                        resultados[clave] = resultados.get(clave, 0) + 1
        return sorted(resultados.items(), key=lambda x: x[1], reverse=True)

    elif modo == "inverso":
        secuencias = []
        for item in data_filtrada:
            if tipo == "fijos":
                digitos = item["fijos"][0]
            else:
                digitos = item["numbers"].replace("-", "")
            colores = [COLOR_MAP[d] for d in digitos if d in COLOR_MAP]
            if len(colores) == salto:
                secuencias.append(tuple(colores))

        plano = [color for grupo in secuencias for color in grupo]

        for i in range(len(plano) - tam):
            if plano[i:i+tam] == secuencia_usuario:
                anterior = plano[i - salto:i] if i >= salto else []
                siguiente = plano[i + tam:i + tam + salto] if i + tam + salto <= len(plano) else []
                if anterior and siguiente:
                    clave = f"{','.join(anterior)}→{','.join(siguiente)}"
                    resultados[clave] = resultados.get(clave, 0) + 1

        return sorted(resultados.items(), key=lambda x: x[1], reverse=True)


    return []
