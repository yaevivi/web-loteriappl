import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os
from datetime import datetime

URL = "https://bolitadivinanza.com/adivinanza/"
JSON_FILENAME = "data/adivinanzas.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def convertir_fecha(fecha_texto):
    """Convierte '04 de Junio de 2025' → '04/06/25'."""
    meses = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    try:
        partes = fecha_texto.lower().replace("  ", " ").split(" de ")
        if len(partes) == 3:
            dia = partes[0].zfill(2)
            mes = meses[partes[1]]
            año = partes[2][-2:]  # últimos 2 dígitos del año
            return f"{dia}/{mes}/{año}"
    except Exception as e:
        print(f"[Error al convertir fecha] {fecha_texto} -> {e}")
    return None

def obtener_y_guardar_adivinanza():
    # Descargar HTML
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return f"Error al descargar la página: {response.status_code}"

    # Leer y parsear HTML
    soup = BeautifulSoup(response.text, "html.parser")

    content_div = soup.find("div", class_="entry-content is-layout-flow")
    if not content_div:
        os.remove(HTML_FILENAME)
        return "No se encontró el contenido de adivinanza."

    # Extraer <p> y aplicar excepción para el título de la fecha
    paragraphs = content_div.find_all("p")
    textos = []
    for p in paragraphs:
        raw_text = p.get_text(separator=" ", strip=True)
        if "Probabilidad y Adivinanzas" in raw_text:
            raw_text = raw_text.replace("202 5", "2025")  # Excepción específica
        if raw_text:
            textos.append(raw_text)

    texto_completo = "\n".join(textos)

    # Extraer campos principales
    fecha_texto = next((t for t in textos if "Probabilidad y Adivinanzas" in t), "")
    fecha_texto = fecha_texto.replace("Probabilidad y Adivinanzas", "").strip()
    clave_json = convertir_fecha(fecha_texto)
    if not clave_json:
        os.remove(HTML_FILENAME)
        return f"Fecha no válida o no reconocida: '{fecha_texto}'"

    numeros = next((t for t in textos if "Probabilidad:" in t), "").replace("Probabilidad:", "").strip()
    claves = next((t for t in textos if "Palabras claves:" in t), "").replace("Palabras claves:", "").strip()
    adivinanza = next((t for t in textos if "🌞" in t), "")
    adivinanza2 = next((t for t in textos if "🌜" in t), "")

    entrada = {
        "probabilidad": numeros.split(", "),
        "palabras_claves": claves.split(", "),
        "adivinanza dia": adivinanza,
        "adivinanza noche": adivinanza2,
    }

    # Cargar o crear JSON
    data = {}
    if Path(JSON_FILENAME).exists():
        with open(JSON_FILENAME, "r", encoding="utf-8") as jf:
            data = json.load(jf)

    if clave_json not in data:
        data[clave_json] = entrada
        with open(JSON_FILENAME, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, separators=(',', ':'))
    else:
        texto_completo += "\n\n(Entrada ya existente para esta fecha)"

   

    #print(texto_completo)

    #return texto_completo

# Para ejecutar:
# print(obtener_y_guardar_adivinanza())





#if __name__ == "__main__":
#    obtener_y_guardar_adivinanza()
