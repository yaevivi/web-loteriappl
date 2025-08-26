import flet as ft
import os
import json
from core.coti_chiquita import obtener_y_guardar_coti_chiquita

JSON_PATH = "data/coti_chiquita.json"


def coti_chiquita_view(page: ft.Page):
    contenido_text = ft.TextField(
        label="Contenido",
        multiline=True,
        read_only=True,
        min_lines=15,
        expand=True
    )

    def cargar_ultimo_contenido():
        if not os.path.exists(JSON_PATH):
            contenido_text.value = "❌ No se encontró el archivo JSON."
            page.update()
            return

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not datos:
            contenido_text.value = "⚠️ El archivo JSON está vacío."
            page.update()
            return

        ultima_fecha = sorted(datos.keys())[-1]
        contenido = datos[ultima_fecha]["contenido"]
        contenido_text.value = f"📅 Fecha: {ultima_fecha}\n\n{contenido}"
        page.update()

    def actualizar_coti(e):
        contenido_text.value = "⏳ Actualizando..."
        page.update()
        resultado = obtener_y_guardar_coti_chiquita()
        if resultado:
            contenido_text.value = f"⚠️ {resultado}"
        else:
            cargar_ultimo_contenido()
        page.update()

    # Cargar contenido inicial
    cargar_ultimo_contenido()

    return ft.View(
        route="/coti_chiquita",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                        ft.ElevatedButton("🔄 Actualizar", on_click=actualizar_coti)
                    ], spacing=10),
                    contenido_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
