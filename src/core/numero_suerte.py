from bs4 import BeautifulSoup
import requests
import os
import re
import json
from pathlib import Path

# Configuración
URL = "https://bolitadivinanza.com/numeros-de-la-suerte-%f0%9f%8d%80/"
IMG_DIR = "img-temp"
JSON_FILENAME = "data/numeros_suerte.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Asegurar carpeta de imágenes
os.makedirs(IMG_DIR, exist_ok=True)

def extraer_numeros_suerte():
    # Descargar HTML
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return f"Error al descargar la página: {response.status_code}"
    
    # Leer HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extraer imagen principal
    img_tag = soup.find("img", class_="wp-post-image")
    img_url = img_tag["src"] if img_tag else None

    # Extraer texto y fecha
    content_div = soup.find("div", class_="entry-content is-layout-flow")
    fecha_tag = content_div.find("p")
    fecha_texto = fecha_tag.get_text(strip=True) if fecha_tag else "sin_fecha"
    fecha_texto = re.sub(r"[^\d/]", "", fecha_texto)  # Eliminar símbolos no numéricos
    try:
        dia, mes, anio = fecha_texto.split("/")
        clave_fecha = f"{dia}/{mes}/{anio[-2:]}"
    except Exception:
        clave_fecha = fecha_texto

    summary_tag = content_div.find("summary")
    texto_resumen = summary_tag.get_text(separator="\n", strip=True) if summary_tag else "Contenido no encontrado"

    # Descargar imagen
    if img_url:
        img_filename = f"{clave_fecha.replace('/', '-')}.jpg"
        img_local_path = os.path.join(IMG_DIR, img_filename)
        if not os.path.exists(img_local_path):
            img_data = requests.get(img_url).content
            with open(img_local_path, "wb") as img_file:
                img_file.write(img_data)

    # Cargar o crear JSON
    data = {}
    if Path(JSON_FILENAME).exists():
        with open(JSON_FILENAME, "r", encoding="utf-8") as jf:
            data = json.load(jf)

    if clave_fecha not in data:
        data[clave_fecha] = {
            "contenido": texto_resumen,
            "imagen_url": img_url
        }
        with open(JSON_FILENAME, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, separators=(',', ':'))

    

    #return f"{clave_fecha}\n\n{texto_resumen}\n\nImagen: {img_url}"

# Ejecutar
#print(extraer_numeros_suerte())
