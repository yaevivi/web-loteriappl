import json
from collections import Counter, defaultdict
from datetime import datetime

COLOR_MAP = {
    '0': 'amarillo', '5': 'amarillo',
    '1': 'morado',   '6': 'morado',
    '2': 'verde',    '7': 'verde',
    '3': 'rojo',     '8': 'rojo',
    '4': 'azul',     '9': 'azul'
}

ORDEN_DRAW = {"M": 0, "E": 1, "N": 2}


def cargar_sorteos_json(path="data/sorteos_unificados_con_fijos.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extraer_colores_por_digito(digitos):
    return [COLOR_MAP[d] for d in digitos if d in COLOR_MAP]


def contar_colores_por_posicion(data, tipo="numbers"):
    posiciones = defaultdict(Counter)
    for item in data:
        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)
        for i, color in enumerate(colores):
            posiciones[i][color] += 1
    return posiciones


def color_dominante_por_estado_turno(data, tipo="numbers"):
    resumen = defaultdict(Counter)
    for item in data:
        clave = (item["state"], item["draw"])
        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)
        for c in colores:
            resumen[clave][c] += 1
    return resumen


def detectar_colores_iguales(data, tipo="numbers"):
    resultados = []
    for item in data:
        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)
        if len(set(colores)) == 1:
            resultados.append({
                "fecha": item["date"],
                "estado": item["state"],
                "turno": item["draw"],
                "color": colores[0]
            })
    return resultados


def detectar_rotaciones(data, tipo="numbers", ventana=3):
    secuencias = []
    historial = []
    for item in data:
        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)
        historial.extend(colores)

    rotaciones = defaultdict(int)
    for i in range(len(historial) - ventana):
        sec = tuple(historial[i:i+ventana])
        rotaciones[sec] += 1
    return Counter(rotaciones).most_common()


def resumen_por_fecha(data, tipo="numbers"):
    resultado = {}
    for item in data:
        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)
        resultado[item["date"]] = {
            "estado": item["state"],
            "turno": item["draw"],
            "colores": colores
        }
    return resultado


def predecir_por_frecuencia(data, tipo="numbers"):
    ultimos = data[-10:]  # últimos 10 sorteos
    posiciones = contar_colores_por_posicion(ultimos, tipo)
    prediccion = [posiciones[i].most_common(1)[0][0] for i in range(len(posiciones))]
    return prediccion


def color_dominante_por_posicion_estado_turno(data, tipo="numbers"):
    """
    Retorna un dict: {(estado, turno): [Counter(), Counter(), Counter()]}  # uno por posición
    """
    resultado = defaultdict(lambda: [Counter(), Counter(), Counter()])
    for item in data:
        estado = item["state"]
        turno = item["draw"]
        clave = (estado, turno)

        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)

        for i, color in enumerate(colores[:3]):  # solo 3 posiciones
            resultado[clave][i][color] += 1

    return resultado


def reglas_temporales_colores(data, tipo="numbers"):
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    colores_por_dia = defaultdict(Counter)
    repeticiones_cada_n = defaultdict(list)

    fechas_colores = []

    for item in data:
        fecha = datetime.strptime(item["date"], "%d/%m/%y")
        dia_nombre = dias_semana[fecha.weekday()]

        digitos = item["fijos"][0] if tipo == "fijos" else item["numbers"].replace("-", "")
        colores = extraer_colores_por_digito(digitos)

        for c in colores:
            colores_por_dia[dia_nombre][c] += 1

        fechas_colores.append((fecha, tuple(colores)))

    # Analizar repeticiones por fechas cíclicas (cada 3 o 7 días)
    fechas_colores.sort()
    for i in range(len(fechas_colores)):
        for j in range(i + 1, len(fechas_colores)):
            delta = (fechas_colores[j][0] - fechas_colores[i][0]).days
            if fechas_colores[i][1] == fechas_colores[j][1] and delta in [3, 7]:
                repeticiones_cada_n[delta].append({
                    "fecha1": fechas_colores[i][0].strftime("%d/%m/%y"),
                    "fecha2": fechas_colores[j][0].strftime("%d/%m/%y"),
                    "colores": fechas_colores[i][1]
                })


    return colores_por_dia, repeticiones_cada_n

