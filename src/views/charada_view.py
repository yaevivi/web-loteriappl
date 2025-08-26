import flet as ft
from core.charada_utils import buscar_por_numero, buscar_por_palabra, sugerencias
import threading

def charada_view(page: ft.Page):
    actualizando = False
    busqueda_timer = None

    # Campo de búsqueda
    input_busqueda = ft.TextField(
        label="Buscar número o palabra",
        hint_text="Ej: 04 o gato",
        expand=True,
        on_change=lambda e: debounce_sugerencias(e.control.value)
    )

    # Lista de sugerencias automáticas
    lista_sugerencias = ft.ListView(
        spacing=5,
        auto_scroll=False,
        height=150,
        visible=False
    )

    # Resultados
    resultado_text = ft.TextField(
        label="Resultado",
        multiline=True,
        read_only=True,
        min_lines=10,
        expand=True
    )

    # Botón para búsqueda manual
    boton_buscar = ft.ElevatedButton(
        "🔍 Buscar",
        on_click=lambda e: mostrar_resultado(input_busqueda.value)
    )

    # Función para ejecutar sugerencias con retraso
    def debounce_sugerencias(valor):
        nonlocal busqueda_timer
        if busqueda_timer:
            busqueda_timer.cancel()
        busqueda_timer = threading.Timer(0.4, lambda: actualizar_sugerencias(valor))
        busqueda_timer.start()

    # Actualizar lista de sugerencias
    def actualizar_sugerencias(valor):
        nonlocal actualizando
        valor = valor.strip()
        if not valor:
            lista_sugerencias.visible = False
            lista_sugerencias.controls.clear()
            page.update()
            return

        sugerencias_encontradas = sugerencias(valor)
        lista_sugerencias.controls.clear()
        for sugerencia in sugerencias_encontradas:
            lista_sugerencias.controls.append(
                ft.ListTile(
                    title=ft.Text(sugerencia),
                    on_click=lambda e, s=sugerencia: seleccionar_sugerencia(s)
                )
            )
        lista_sugerencias.visible = bool(sugerencias_encontradas)
        page.update()

    # Selección desde sugerencias
    def seleccionar_sugerencia(sugerencia):
        nonlocal actualizando
        actualizando = True
        input_busqueda.value = sugerencia
        lista_sugerencias.visible = False
        lista_sugerencias.controls.clear()
        mostrar_resultado(sugerencia)
        actualizando = False
        page.update()

    # Mostrar resultado de la búsqueda
    def mostrar_resultado(valor):
        valor = valor.strip()
        if not valor:
            resultado_text.value = "❌ Ingresa un número o palabra para buscar."
            page.update()
            return

        if valor.isdigit():
            resultado = buscar_por_numero(valor)
            if resultado:
                resultado_text.value = "\n".join([f"🔹 {r}" for r in resultado])
            else:
                resultado_text.value = "⚠️ No se encontraron resultados para ese número."
        else:
            resultado = buscar_por_palabra(valor)
            if resultado:
                resultado_text.value = "\n".join([f'🔹 {item["palabra"]}: {item["numeros"]}' for item in resultado])
            else:
                resultado_text.value = "⚠️ No se encontraron coincidencias con esa palabra."

        page.update()

    return ft.View(
        route="/charada",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                    input_busqueda,
                    boton_buscar,
                    lista_sugerencias,
                    resultado_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
