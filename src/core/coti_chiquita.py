from bs4 import BeautifulSoup
from pathlib import Path
import json
import os
import requests

# Configuración
URL = "https://bolitadivinanza.com/la-coti-chiquita/"
JSON_FILENAME = "data/coti_chiquita.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def obtener_y_guardar_coti_chiquita():
    # Descargar HTML
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return f"Error al descargar la página: {response.status_code}"

    # Leer y parsear HTML
    soup = BeautifulSoup(response.text, "html.parser")

    content_div = soup.find("div", class_="entry-content is-layout-flow")
    if not content_div:
        os.remove(HTML_FILENAME)
        return "No se encontró el contenido de Coti Chiquita."

    # Extraer fecha (en formato dd/mm/yy)
    fecha_tag = content_div.find("p")
    fecha_texto = fecha_tag.get_text(strip=True) if fecha_tag else "sin_fecha"

    # Convertir a formato clave: "04/06/25"
    try:
        dia, mes, anio = fecha_texto.split("/")
        clave_fecha = f"{dia}/{mes}/{anio[-2:]}"
    except Exception:
        clave_fecha = fecha_texto  # fallback si el formato falla

    # Extraer <summary> con separadores
    summary_tag = content_div.find("summary")
    if not summary_tag:
        os.remove(HTML_FILENAME)
        return "No se encontró el resumen de contenido."

    texto_resumen = summary_tag.get_text(separator="\n", strip=True)

    entrada = {
        "contenido": texto_resumen
    }

    # Cargar JSON o crear uno nuevo
    data = {}
    if Path(JSON_FILENAME).exists():
        with open(JSON_FILENAME, "r", encoding="utf-8") as jf:
            data = json.load(jf)

    if clave_fecha not in data:
        data[clave_fecha] = entrada
        with open(JSON_FILENAME, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, separators=(',', ':'))
    else:
        texto_resumen += "\n\n(Entrada ya existente para esta fecha)"

    

    #return f"{clave_fecha}\n\n{texto_resumen}"

# Ejecutar
#if __name__ == "__main__":
#    print(obtener_y_guardar_coti_chiquita())
