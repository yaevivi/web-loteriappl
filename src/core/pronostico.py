from bs4 import BeautifulSoup
from pathlib import Path
import json
import os
import requests
import re

# Configuración
URL = "https://bolitadivinanza.com/"
JSON_FILENAME = "data/pronostico.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def obtener_y_guardar_pronostico():
    # Descargar página principal
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return f"Error al descargar la página: {response.status_code}"

    # Cargar y parsear HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar artículo por texto distintivo
    articles = soup.find_all("article", class_="entry-card")
    bloque = None
    for art in articles:
        if "Pronosticando los Números" in art.text:
            bloque = art
            break

    if not bloque:
        os.remove(HTML_FILENAME)
        return "No se encontró el artículo de pronóstico."

    summary_tag = bloque.find("summary")
    if not summary_tag:
        os.remove(HTML_FILENAME)
        return "No se encontró el resumen dentro del artículo."

    texto_completo = summary_tag.get_text(separator="\n", strip=True)

    # Buscar fecha en el texto
    match_fecha = re.search(r"D[ií]a (\d{2})-(\d{2})-(\d{4})", texto_completo)
    if not match_fecha:
        os.remove(HTML_FILENAME)
        return "No se pudo extraer la fecha del pronóstico."

    dia, mes, anio = match_fecha.groups()
    clave_fecha = f"{dia}/{mes}/{anio[-2:]}"  # dd/mm/yy

    # Preparar entrada
    entrada = {"contenido": texto_completo}

    # Cargar o crear JSON
    data = {}
    if Path(JSON_FILENAME).exists():
        with open(JSON_FILENAME, "r", encoding="utf-8") as jf:
            data = json.load(jf)

    if clave_fecha not in data:
        data[clave_fecha] = entrada
        with open(JSON_FILENAME, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, separators=(',', ':'))
    else:
        texto_completo += "\n\n(Entrada ya existente)"

    
    #return f"{clave_fecha}\n\n{texto_completo}"

# Ejecutar
if __name__ == "__main__":
    print(obtener_y_guardar_pronostico())
