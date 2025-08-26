import flet as ft
from core.cadena_utils import obtener_cadena

def cadena_charada_view(page: ft.Page):
    input_numero = ft.TextField(
        label="Número de la charada (00-99)",
        hint_text="Ej: 03",
        max_length=2,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True
    )

    resultado_text = ft.TextField(
        label="Sugerencias de la cadena",
        multiline=True,
        read_only=True,
        min_lines=10,
        expand=True
    )
    

    def mostrar_cadena(e):
        numero = input_numero.value.strip().zfill(2)
        if not numero.isdigit() or not (0 <= int(numero) <= 99):
            resultado_text.value = "❌ Ingresa un número del 00 al 99."
            page.update()
            return

        resultado = obtener_cadena(numero)
        if resultado is None:
            resultado_text.value = "⚠️ No se encontró la cadena para ese número."
        else:
            base = resultado["base"]
            sugerencias = resultado["sugerencias"]

            texto = f"✨ Después de {base['number']} - {base['word']} {base['icon']} se puede jugar:\n\n"
            for item in sugerencias:
                texto += f"{item['number']} - {item['word']} {item['icon']}\n"

            resultado_text.value = texto

        page.update()

    return ft.View(
        route="/cadena",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                    input_numero,
                    ft.ElevatedButton("🎲 Ver cadena sugerida", on_click=mostrar_cadena),
                    resultado_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
