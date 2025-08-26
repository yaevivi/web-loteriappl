import flet as ft
import json
import os
from core.los_pasos import obtener_y_guardar_los_pasos

JSON_PATH = "data/los_pasos.json"

def los_pasos_view(page: ft.Page):
    resultado_text = ft.TextField(
        label="Contenido Los Pasos",
        multiline=True,
        read_only=True,
        min_lines=20,
        expand=True
    )

    def cargar_ultimo():
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                ultima_fecha = sorted(data.keys())[-1]
                resultado_text.value = f"📅 Fecha: {ultima_fecha}\n\n{data[ultima_fecha]['contenido']}"
            else:
                resultado_text.value = "⚠️ No hay datos disponibles."
        else:
            resultado_text.value = "❌ Archivo JSON no encontrado."

    def actualizar(e):
        resultado_text.value = "⏳ Actualizando..."
        page.update()
        try:
            obtener_y_guardar_los_pasos()
            cargar_ultimo()
        except Exception as ex:
            resultado_text.value = f"❌ Error: {ex}"
        page.update()

    cargar_ultimo()

    return ft.View(
        route="/los_pasos",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar", on_click=actualizar),
                    resultado_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
