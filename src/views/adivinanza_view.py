import flet as ft
from core.adivinanza import obtener_y_guardar_adivinanza
import json
import os

RUTA_JSON = "data/adivinanzas.json"

def adivinanza_view(page: ft.Page):
    resultado = ft.TextField(
        label="Resultado",
        multiline=True,
        read_only=True,
        min_lines=10,
        expand=True,
    )

    def actualizar(e):
        resultado.value = "⏳ Actualizando..."
        page.update()
        obtener_y_guardar_adivinanza()
        resultado.value = cargar_ultimo_texto()
        page.update()

    def cargar_ultimo_texto():
        if not os.path.exists(RUTA_JSON):
            return "❌ No hay datos."
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return "❌ JSON vacío."
        ultima_fecha = sorted(data.keys())[-1]
        registro = data[ultima_fecha]
        texto = f"📅 {ultima_fecha}\n"
        texto += f"🔢 Probabilidad: {', '.join(registro['probabilidad'])}\n"
        texto += f"🗝️ Claves: {', '.join(registro['palabras_claves'])}\n"
        texto += f"{registro.get('adivinanza dia', '')}\n{registro.get('adivinanza noche', '')}"
        return texto

    resultado.value = cargar_ultimo_texto()

    return ft.View(
        route="/adivinanza",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/adivinanzas")),
                    ft.ElevatedButton("🔄 Actualizar", on_click=actualizar),
                    resultado
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
