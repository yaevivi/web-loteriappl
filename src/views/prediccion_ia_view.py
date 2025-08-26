import flet as ft
from core.modelo_fijo_mlp_ia import predecir_fijos_ia


def prediccion_ia_view(page: ft.Page):
    estados = ["FL", "GA", "NY"]
    horarios_por_estado = {
        "GA": ["M", "E", "N"],
        "FL": ["M", "E"],
        "NY": ["M", "E"]
    }
    tops = [5, 10, 20, 30]

    dropdown_estado = ft.Dropdown(
        label="Estado",
        options=[ft.dropdown.Option(e) for e in estados],
        expand=True
    )

    dropdown_draw = ft.Dropdown(
        label="Turno",
        options=[],
        expand=True
    )

    dropdown_top_n = ft.Dropdown(
        label="Top N",
        options=[ft.dropdown.Option(str(n)) for n in tops],
        value="5",
        expand=True
    )

    input_fecha = ft.TextField(label="Fecha (dd/mm/aa)", hint_text="Ej: 27/05/25", expand=True)
    resultado_text = ft.TextField(label="Resultados", multiline=True, read_only=True, min_lines=10, expand=True)
   

    def actualizar_horarios(e):
        estado = dropdown_estado.value
        if estado:
            horarios = horarios_por_estado.get(estado, [])
            dropdown_draw.options = [ft.dropdown.Option(h) for h in horarios]
            dropdown_draw.value = None
            page.update()

    dropdown_estado.on_change = actualizar_horarios

    def ejecutar_prediccion(e):
        fecha = input_fecha.value.strip()
        estado = dropdown_estado.value
        draw = dropdown_draw.value
        try:
            top_n = int(dropdown_top_n.value or 5)
        except:
            top_n = 5

        if not fecha or not estado or not draw:
            resultado_text.value = "❌ Por favor completa todos los campos correctamente."
            page.update()
            return

        try:
            predicciones = predecir_fijos_ia(fecha, estado, draw, top_n=top_n)
            if not predicciones:
                resultado_text.value = "⚠️ No se encontraron predicciones."
            else:
                resultado_text.value = "\n".join([
                    f"🔹 Fijo: {item['fijo']} | Probabilidad: {round(float(item['prob']) * 100, 2)}%"
                    for item in predicciones
                ])
        except Exception as ex:
            resultado_text.value = f"❌ Error: {ex}"

        page.update()

    return ft.View(
        route="/ia",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                    input_fecha,
                    dropdown_estado,
                    dropdown_draw,
                    dropdown_top_n,
                    ft.Row([
                        ft.ElevatedButton("🧠 Predecir con IA", on_click=ejecutar_prediccion),
                    ]),
                    resultado_text
                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
