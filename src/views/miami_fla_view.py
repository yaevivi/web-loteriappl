import flet as ft
import json
import os
from core.miami_fla import obtener_y_guardar_miami_fla

JSON_PATH = "data/miami_fla.json"

def miami_fla_view(page: ft.Page):
    contenido_text = ft.TextField(
        label="Contenido de Miami FLA",
        multiline=True,
        read_only=True,
        min_lines=20,
        expand=True,
    )

    def cargar_ultimo_contenido():
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos:
                    ultima_fecha = sorted(datos.keys())[-1]
                    contenido = datos[ultima_fecha]["contenido"]
                    contenido_text.value = f"📅 Fecha: {ultima_fecha}\n\n{contenido}"
                else:
                    contenido_text.value = "⚠️ No hay contenido disponible."
        else:
            contenido_text.value = "⚠️ Archivo JSON no encontrado."

    def actualizar_datos(e):
        contenido_text.value = "⏳ Actualizando..."
        page.update()
        resultado = obtener_y_guardar_miami_fla()
        if resultado:
            contenido_text.value = f"❌ Error: {resultado}"
        else:
            cargar_ultimo_contenido()
        page.update()

    # Cargar al iniciar
    cargar_ultimo_contenido()

    return ft.View(
        route="/miami_fla",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar", on_click=actualizar_datos),
                    contenido_text
                ], spacing=15, scroll="auto", expand=True),
                expand=True
            )
        ]
    )
