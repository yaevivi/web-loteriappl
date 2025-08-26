import os
import json

CHARADA_NUM_PATH = os.path.join("data", "charada.json")
CHARADA_PALABRA_PATH = os.path.join("data", "CharadaPalabra.json")

charada_por_numero = {}
charada_por_palabra = {}

# ✨ Cargar datos una sola vez
def cargar_charadas():
    global charada_por_numero, charada_por_palabra
    with open(CHARADA_NUM_PATH, "r", encoding="utf-8") as f:
        charada_por_numero = json.load(f)
    with open(CHARADA_PALABRA_PATH, "r", encoding="utf-8") as f:
        charada_por_palabra = json.load(f)

# 🔍 Buscar por número
def buscar_por_numero(numero: str):
    numero = str(int(numero)).zfill(2)  # Asegura dos dígitos
    print(numero)
    resultado = charada_por_numero.get(numero)
    return resultado if resultado else []

# 🔍 Buscar por palabra (insensible a mayúsculas y parcial)
def buscar_por_palabra(palabra: str):
    palabra = palabra.strip().lower()
    coincidencias = []
    for letra, lista in charada_por_palabra.items():
        for item in lista:
            nombre = item["palabra"].lower()
            if palabra in nombre:
                coincidencias.append({
                    "palabra": item["palabra"],
                    "numeros": item["numeros"]
                })
    return coincidencias

# 🖉 Autocompletado para el campo de entrada
def sugerencias(parcial: str):
    parcial = parcial.strip().lower()
    sugerencias = set()
    if parcial.isdigit():
        for numero in charada_por_numero.keys():
            if numero.startswith(parcial):
                sugerencias.add(numero)
    else:
        for letra, lista in charada_por_palabra.items():
            for item in lista:
                palabra = item["palabra"].lower()
                if parcial in palabra:
                    sugerencias.add(item["palabra"])
    return sorted(list(sugerencias))

# 🔄 Inicializar
cargar_charadas()
