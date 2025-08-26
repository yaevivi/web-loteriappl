import flet as ft
from datetime import datetime
from core.prediccion_colores import predecir_por_secuencia_colores

ESTADOS = ["FL", "GA", "NY"]
DRAWS_TODOS = ["M", "E", "N"]
DRAWS_POR_ESTADO = {
    "FL": ["M", "E"],
    "GA": ["M", "E", "N"],
    "NY": ["M", "E"]
}
MODOS = ["normal", "inverso"]
TIPOS = ["fijos", "numbers"]
SECUENCIAS = {
    "fijos": ["2", "4", "6", "8"],
    "numbers": ["3", "6", "9", "12"]
}

COLOR_ICONS = {
    "amarillo": "icons/am.png",
    "rojo": "icons/r.png",
    "azul": "icons/az.png",
    "verde": "icons/v.png",
    "morado": "icons/m.png"
}

STATE_ICONS = {
    "FL": "icons/fl.png",
    "GA": "icons/ga.png",
    "NY": "icons/ny.png"
}

DRAW_ICONS = {
    "M": "icons/md.png",
    "E": "icons/ev.png",
    "N": "icons/ng.png"
}

COLOR_CHOICES = list(COLOR_ICONS.keys())

def colores_view(page: ft.Page):
    dropdown_tipo = ft.Dropdown(label="Tipo de dato", options=[ft.dropdown.Option(t) for t in TIPOS], value="fijos", expand=True)
    dropdown_modo = ft.Dropdown(label="Modo", options=[ft.dropdown.Option(m) for m in MODOS], value="normal", expand=True)
    dropdown_tamanio = ft.Dropdown(label="Tamaño de secuencia", options=[ft.dropdown.Option(s) for s in SECUENCIAS["fijos"]], value="2", expand=True)

    check_estados = [ft.Checkbox(label=estado, value=True) for estado in ESTADOS]
    check_draws = [ft.Checkbox(label=draw, value=True) for draw in DRAWS_TODOS]

    def actualizar_tamanio(e):
        tipo = dropdown_tipo.value
        dropdown_tamanio.options = [ft.dropdown.Option(s) for s in SECUENCIAS[tipo]]
        dropdown_tamanio.value = SECUENCIAS[tipo][0]
        page.update()

    dropdown_tipo.on_change = actualizar_tamanio

    def actualizar_turnos(*_):
        seleccionados = [c.label for c in check_estados if c.value]
        disponibles = set()
        for est in seleccionados:
            disponibles.update(DRAWS_POR_ESTADO.get(est, []))
        for cb in check_draws:
            cb.visible = cb.label in disponibles
        page.update()

    for cb in check_estados:
        cb.on_change = actualizar_turnos

    estados_fila = ft.Row([
        ft.Column([
            ft.Image(src=STATE_ICONS[estado], width=30, height=30),
            check_estados[i]
        ]) for i, estado in enumerate(ESTADOS)
    ])

    draws_fila = ft.Row([
        ft.Column([
            ft.Image(src=DRAW_ICONS[draw], width=30, height=30),
            check_draws[i]
        ]) for i, draw in enumerate(DRAWS_TODOS)
    ])

    selected_secuencia = ft.Row(wrap=True, spacing=5, scroll="auto")
    resultado_visual = ft.Column(scroll="auto", expand=True)    
    colores_actuales = []

    def agregar_color(c):
        if len(colores_actuales) >= int(dropdown_tamanio.value):
            return
        colores_actuales.append(c)
        actualizar_visual_secuencia()

    def limpiar_colores(e):
        colores_actuales.clear()
        actualizar_visual_secuencia()

    def actualizar_visual_secuencia():
        selected_secuencia.controls.clear()
        for color in colores_actuales:
            selected_secuencia.controls.append(
                ft.Container(
                    content=ft.Image(src=COLOR_ICONS[color], width=40, height=40),
                    padding=4,
                    border=ft.border.all(2, ft.Colors.BLACK),
                    border_radius=6,
                    bgcolor="white"
                )
            )
        page.update()

    input_fecha_ini = ft.TextField(label="Fecha inicio", read_only=True, expand=True)
    input_fecha_fin = ft.TextField(label="Fecha fin", read_only=True, expand=True)

    def on_fecha_ini_change(e):
        input_fecha_ini.value = e.control.value.strftime("%d/%m/%y")
        page.update()

    def on_fecha_fin_change(e):
        input_fecha_fin.value = e.control.value.strftime("%d/%m/%y")
        page.update()

    date_ini_picker = ft.DatePicker(on_change=on_fecha_ini_change)
    date_fin_picker = ft.DatePicker(on_change=on_fecha_fin_change)
    page.overlay.extend([date_ini_picker, date_fin_picker])

    def generar_fila_colores(colores):
        return ft.Row([
            ft.Container(
                content=ft.Image(src=COLOR_ICONS[c], width=30, height=30),
                padding=2,
                bgcolor="white",
                border=ft.border.all(1, ft.Colors.BLACK),
                border_radius=4
            ) for c in colores
        ], wrap=True)

    def ejecutar_prediccion(e):
        tipo = dropdown_tipo.value
        modo = dropdown_modo.value
        tamanio = int(dropdown_tamanio.value)
        estados = [c.label for c in check_estados if c.value]
        draws = [c.label for c in check_draws if c.visible and c.value]
        fecha_ini = input_fecha_ini.value.strip() or None
        fecha_fin = input_fecha_fin.value.strip() or None

        secuencia = colores_actuales.copy()

        if len(secuencia) != tamanio:
            resultado_visual.controls = [ft.Text(f"❌ Debes seleccionar exactamente {tamanio} colores.", color=ft.Colors.RED)]
            page.update()
            return

        try:
            r = predecir_por_secuencia_colores(
                secuencia_usuario=secuencia,
                tipo=tipo,
                tam=tamanio,
                modo=modo,
                estados=estados,
                horarios=draws,
                desde=fecha_ini,
                hasta=fecha_fin
            )

            if not r:
                resultado_visual.controls = [ft.Text("⚠️ No se encontraron coincidencias para la secuencia dada.", color=ft.Colors.ORANGE)]
                page.update()
                return

            resultado_visual.controls = [ft.Text("🎯 Secuencia ingresada:")]
            resultado_visual.controls.append(generar_fila_colores(secuencia))

            if modo == "normal":
                resultado_visual.controls.append(ft.Text("\n🔮 Colores siguientes más frecuentes:"))
                for siguiente, freq in r:
                    fila = ft.Row([
                        generar_fila_colores(siguiente),
                        ft.Text(f": {freq} veces")
                    ])
                    resultado_visual.controls.append(fila)
            else:
                resultado_visual.controls.append(ft.Text("\n🔄 Combinaciones previas y siguientes:"))
                for clave, freq in r:
                    ant_str, sig_str = clave.split("→")
                    ant = ant_str.split(",")
                    sig = sig_str.split(",")
                    fila = ft.Row([
                        generar_fila_colores(ant),
                        ft.Text(" → "),
                        generar_fila_colores(sig),
                        ft.Text(f": {freq} veces")
                    ])
                    resultado_visual.controls.append(fila)

        except Exception as ex:
            resultado_visual.controls = [ft.Text(f"❌ Error: {ex}", color=ft.Colors.RED)]

        page.update()

    actualizar_turnos()

    return ft.View(
        route="/colores",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                    ft.Row([dropdown_tipo, dropdown_modo, dropdown_tamanio]),
                    ft.Text("✔️ Estados a incluir:"),
                    estados_fila,
                    ft.Text("⏱️ Turnos a incluir:"),
                    draws_fila,
                    ft.Row([
                        input_fecha_ini,
                        ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: (setattr(date_ini_picker, "open", True), page.update())),
                        input_fecha_fin,
                        ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: (setattr(date_fin_picker, "open", True), page.update())),
                    ]),
                    ft.Text("🎨 Selecciona colores para la secuencia:"),
                    ft.Row([
                        ft.ElevatedButton("🟡 Amarillo", on_click=lambda e: agregar_color("amarillo")),
                        ft.ElevatedButton("🔴 Rojo", on_click=lambda e: agregar_color("rojo")),
                        ft.ElevatedButton("🔵 Azul", on_click=lambda e: agregar_color("azul")),
                        ft.ElevatedButton("🟢 Verde", on_click=lambda e: agregar_color("verde")),
                        ft.ElevatedButton("🟣 Morado", on_click=lambda e: agregar_color("morado")),
                        ft.IconButton(icon=ft.Icons.DELETE, tooltip="Limpiar", on_click=limpiar_colores),
                    ], wrap=True),
                    selected_secuencia,
                    ft.ElevatedButton("🔍 Buscar Patrón", on_click=ejecutar_prediccion),
                    ft.Row(controls=[resultado_visual], scroll="auto", expand=True)
                    
                ], scroll="auto", spacing=15, expand=True),
                expand=True
            )
        ]
    )
