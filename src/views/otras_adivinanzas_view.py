import flet as ft
import json
import os
from core.otras_adivinanzas import obtener_y_guardar_otras_adivinanzas

RUTA_JSON = "data/otras_adivinanzas.json"

def otras_adivinanzas_view(page: ft.Page):
    contenido_text = ft.TextField(
        label="Última Adivinanza",
        multiline=True,
        read_only=True,
        min_lines=15,
        expand=True,
    )

    def cargar_ultima_entrada():
        if not os.path.exists(RUTA_JSON):
            contenido_text.value = "⚠️ No se encontró el archivo de adivinanzas."
            return

        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            contenido_text.value = "⚠️ No hay entradas en el archivo."
            return

        ultima_fecha = sorted(data.keys())[-1]
        contenido = data[ultima_fecha]["contenido"]
        contenido_text.value = f"📅 Fecha: {ultima_fecha}\n\n{contenido}"

    def actualizar(e):
        contenido_text.value = "⏳ Actualizando..."
        page.update()
        log = obtener_y_guardar_otras_adivinanzas()
        if log:
            contenido_text.value = f"⚠️ {log}"
        else:
            cargar_ultima_entrada()
        page.update()

    # Cargar al entrar
    cargar_ultima_entrada()

    return ft.View(
        route="/otras_adivinanzas",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar", on_click=actualizar),
                    contenido_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
