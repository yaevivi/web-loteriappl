import flet as ft
import json
import os
from core.numero_suerte import extraer_numeros_suerte

JSON_PATH = "data/numeros_suerte.json"
IMG_PATH = "img-temp"


def numero_suerte_view(page: ft.Page):
    resultado_text = ft.TextField(label="Contenido", multiline=True, read_only=True, min_lines=15, expand=True)
    imagen_widget = ft.Image(width=300, height=300, fit=ft.ImageFit.CONTAIN)

    def cargar_ultimo_registro():
        if not os.path.exists(JSON_PATH):
            resultado_text.value = "❌ No se encontró el archivo de datos."
            return

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not datos:
            resultado_text.value = "⚠️ No hay entradas registradas."
            return

        ultima_fecha = sorted(datos.keys())[-1]
        entrada = datos[ultima_fecha]
        contenido = entrada.get("contenido", "(Sin contenido)")
        imagen_url = entrada.get("imagen_url")

        resultado_text.value = f"📅 Fecha: {ultima_fecha}\n\n{contenido}"

        # Mostrar imagen local
        imagen_archivo = os.path.join(IMG_PATH, f"{ultima_fecha.replace('/', '-')}.jpg")
        if os.path.exists(imagen_archivo):
            imagen_widget.src = imagen_archivo
        else:
            imagen_widget.src = None

    def actualizar(e):
        resultado_text.value = "⏳ Actualizando..."
        page.update()
        extraer_numeros_suerte()
        cargar_ultimo_registro()
        page.update()

    # Cargar al entrar
    cargar_ultimo_registro()

    return ft.View(
        route="/numero_suerte",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar Números de la Suerte", on_click=actualizar),
                    imagen_widget,
                    resultado_text
                ], spacing=15, scroll="auto", expand=True),
                expand=True
            )
        ]
    )
