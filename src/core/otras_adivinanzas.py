from bs4 import BeautifulSoup
from pathlib import Path
import json
import os
import requests
import re

# Configuración
URL = "https://bolitadivinanza.com/otras-adivinanzas/"
JSON_FILENAME = "data/otras_adivinanzas.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def obtener_y_guardar_otras_adivinanzas():
    # Descargar página específica
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return f"Error al descargar la página: {response.status_code}"

    # Parsear HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Obtener la fecha
    fecha_tag = soup.find("p", class_="has-text-align-center")
    fecha_str = fecha_tag.get_text(strip=True) if fecha_tag else None
    match_fecha = re.match(r"(\d{2})/(\d{2})/(\d{4})", fecha_str) if fecha_str else None

    if not match_fecha:
        os.remove(HTML_FILENAME)
        return "No se pudo extraer la fecha."

    dia, mes, anio = match_fecha.groups()
    clave_fecha = f"{dia}/{mes}/{anio[-2:]}"  # dd/mm/yy

    # Extraer el contenido principal
    summary_tag = soup.find("summary")
    if not summary_tag:
        os.remove(HTML_FILENAME)
        return "No se encontró el contenido principal."

    texto_completo = summary_tag.get_text(separator="\n", strip=True)

    # Preparar entrada
    entrada = {"contenido": texto_completo}

    # Cargar JSON si existe
    data = {}
    if Path(JSON_FILENAME).exists():
        with open(JSON_FILENAME, "r", encoding="utf-8") as jf:
            data = json.load(jf)

    # Agregar entrada si no está
    if clave_fecha not in data:
        data[clave_fecha] = entrada
        with open(JSON_FILENAME, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, separators=(',', ':'))
    else:
        texto_completo += "\n\n(Entrada ya existente)"

   

    #return f"{clave_fecha}\n\n{texto_completo}"

# Ejecutar si es main
#if __name__ == "__main__":
#    print(obtener_y_guardar_otras_adivinanzas())
