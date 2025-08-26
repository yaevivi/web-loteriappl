import flet as ft
import json
import os
from core.pronostico import obtener_y_guardar_pronostico

RUTA_JSON = "data/pronostico.json"


def pronostico_view(page: ft.Page):
    resultado_text = ft.TextField(
        label="Contenido del Pronóstico",
        multiline=True,
        read_only=True,
        min_lines=10,
        expand=True
    )

    def mostrar_ultimo_contenido():
        if not os.path.exists(RUTA_JSON):
            resultado_text.value = "⚠️ No se encuentra el archivo de pronóstico."
            return

        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            resultado_text.value = "⚠️ No hay entradas registradas."
            return

        ultima_fecha = sorted(data.keys())[-1]
        contenido = data[ultima_fecha].get("contenido", "Contenido no disponible")

        resultado_text.value = f"📅 Fecha: {ultima_fecha}\n\n{contenido}"

    def actualizar_datos(e):
        resultado_text.value = "⏳ Actualizando..."
        page.update()
        resultado = obtener_y_guardar_pronostico()
        if resultado:
            resultado_text.value = f"⚠️ {resultado}"
        else:
            mostrar_ultimo_contenido()
        page.update()

    # Mostrar al cargar
    mostrar_ultimo_contenido()

    return ft.View(
        route="/pronostico",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar Pronóstico", on_click=actualizar_datos),
                    resultado_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
