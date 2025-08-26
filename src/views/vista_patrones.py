import flet as ft
from core.patrones_colores import (
    contar_colores_por_posicion,
    detectar_colores_iguales,
    detectar_rotaciones,
    predecir_por_frecuencia,
    cargar_sorteos_json,
    color_dominante_por_estado_turno,
    color_dominante_por_posicion_estado_turno,
    reglas_temporales_colores
)

from collections import Counter
from datetime import datetime

COLOR_ICONOS = {
    "amarillo": "icons/am.png",
    "rojo": "icons/r.png",
    "azul": "icons/az.png",
    "verde": "icons/v.png",
    "morado": "icons/m.png"
}

COLOR_RGB = {
    "amarillo": "#FFBF00",
    "rojo": "#FF4C4C",
    "azul": "#4C8CFF",
    "verde": "#4CFF4C",
    "morado": "#BF4CFF"
}

DRAWS_POR_ESTADO = {
    "FL": ["M", "E"],
    "GA": ["M", "E", "N"],
    "NY": ["M", "E"]
}

ESTADOS = ["FL", "GA", "NY"]
DRAWS_TODOS = ["M", "E", "N"]

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

def vista_patrones(page: ft.Page) -> ft.View:
    data_completo = cargar_sorteos_json()
    tipo = "numbers"

    check_estados = [ft.Checkbox(label=estado, value=True) for estado in ESTADOS]
    check_draws = [ft.Checkbox(label=draw, value=True) for draw in DRAWS_TODOS]

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

    input_fecha_ini = ft.TextField(label="Fecha inicio", read_only=True, expand=True)
    input_fecha_fin = ft.TextField(label="Fecha fin", read_only=True, expand=True)
    date_ini_picker = ft.DatePicker(on_change=lambda e: (setattr(input_fecha_ini, "value", e.control.value.strftime("%d/%m/%y")), page.update()))
    date_fin_picker = ft.DatePicker(on_change=lambda e: (setattr(input_fecha_fin, "value", e.control.value.strftime("%d/%m/%y")), page.update()))
    page.overlay.extend([date_ini_picker, date_fin_picker])

    content_column = ft.Column(expand=True)

    def aplicar_filtro(e):
        estados = [c.label for c in check_estados if c.value]
        draws = [c.label for c in check_draws if c.visible and c.value]
        fecha_ini = input_fecha_ini.value.strip()
        fecha_fin = input_fecha_fin.value.strip()

        filtrado = []
        for item in data_completo:
            if estados and item["state"] not in estados:
                continue
            if draws and item["draw"] not in draws:
                continue
            if fecha_ini:
                fi = datetime.strptime(fecha_ini, "%d/%m/%y")
                if datetime.strptime(item["date"], "%d/%m/%y") < fi:
                    continue
            if fecha_fin:
                ff = datetime.strptime(fecha_fin, "%d/%m/%y")
                if datetime.strptime(item["date"], "%d/%m/%y") > ff:
                    continue
            filtrado.append(item)

        if not filtrado:
            content_column.controls = [ft.Text("⚠️ No hay datos para los filtros aplicados", color=ft.Colors.RED)]
            page.update()
            return

        posiciones = contar_colores_por_posicion(filtrado, tipo=tipo)
        repeticiones = detectar_colores_iguales(filtrado, tipo=tipo)
        color_group = Counter([r["color"] for r in repeticiones])
        pred = predecir_por_frecuencia(filtrado, tipo=tipo)

        def render_pie_flet_posicion(data: dict[str, int], title: str) -> ft.Column:
            total = sum(data.values())
            chart_sections = [
                ft.PieChartSection(
                    value=v,
                    title=f"{v / total * 100:.1f}%",
                    title_style=ft.TextStyle(size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                    color=COLOR_RGB.get(k, ft.Colors.GREY),
                    radius=80,
                ) for k, v in data.items()
            ]
            pie_chart = ft.PieChart(
                sections=chart_sections,
                sections_space=2,
                center_space_radius=0,
                width=300,
                height=300,
                expand=False
            )
            return ft.Column([ft.Text(title, size=18, weight="bold"), pie_chart])

        def render_pie_flet(data: dict[str, int], title: str, repeticiones: list[dict]) -> ft.Column:
            total = sum(data.values())
            chart_sections = []
            detalles_colores_local = ft.Column(scroll="auto")

            for k, v in data.items():
                chart_sections.append(
                    ft.PieChartSection(
                        value=v,
                        title=f"{v / total * 100:.1f}%",
                        title_style=ft.TextStyle(size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                        color=COLOR_RGB.get(k, ft.Colors.GREY),
                        radius=80
                    )
                )

            pie_chart = ft.PieChart(
                sections=chart_sections,
                sections_space=2,
                center_space_radius=0,
                width=300,
                height=300,
                expand=False
            )

            def detalles_sections(color: str):
                detalles = [f"{r['fecha']} ({r['estado']}-{r['turno']})" for r in repeticiones if r["color"] == color]
                detalles_colores_local.controls = [
                    ft.Text(f"{color.upper()} → {len(detalles)} ocurrencias", weight="bold", size=16)
                ] + [
                    ft.Container(
                        ft.Text(f"📅 {d}", size=13),
                        bgcolor=COLOR_RGB.get(color, ft.Colors.GREY),
                        padding=5,
                        border_radius=6
                    ) for d in detalles
                ]
                for s in chart_sections:
                    if s.color == COLOR_RGB.get(color, ft.Colors.GREY):
                        s.radius = 105
                        s.title_style = ft.TextStyle(size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                    else:
                        s.radius = 90
                        s.title_style = ft.TextStyle(size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
                pie_chart.sections = chart_sections
                pie_chart.update()
                detalles_colores_local.update()

            def show_detalles():
                for s in chart_sections:
                    s.radius = 90
                    s.title_style = ft.TextStyle(size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
                detalles_colores_local.controls = []
                pie_chart.sections = chart_sections
                pie_chart.update()
                detalles_colores_local.update()

            button_detalles = ft.Row([
                ft.ElevatedButton("🟡 Amarillo", on_click=lambda e: detalles_sections("amarillo")),
                ft.ElevatedButton("🔴 Rojo", on_click=lambda e: detalles_sections("rojo")),
                ft.ElevatedButton("🔵 Azul", on_click=lambda e: detalles_sections("azul")),
                ft.ElevatedButton("🟢 Verde", on_click=lambda e: detalles_sections("verde")),
                ft.ElevatedButton("🟣 Morado", on_click=lambda e: detalles_sections("morado")),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="Limpiar", on_click=lambda e: show_detalles()),
            ], wrap=True)

            return ft.Column([
                ft.Text(title, size=18, weight="bold"),
                pie_chart,
                button_detalles,
                detalles_colores_local
            ])

        analisis_general = ft.Column([
            ft.Text("🎯 Colores más frecuentes por posición", size=20, weight="bold"),
            *[render_pie_flet_posicion(posiciones[i], f"Posición {i+1}") for i in posiciones]
        ], scroll="auto")

        reglas_detectadas = ft.Column([
            ft.Text("🧩 Reglas encontradas", size=20, weight="bold"),
            render_pie_flet(color_group, "Frecuencia de colores homogéneos", repeticiones),
            ft.Divider(),
            ft.Text("🔁 Secuencias rotativas detectadas:", size=16, weight="bold"),
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        *[
                            ft.Image(src=COLOR_ICONOS[c], width=30, height=30)
                            for c in k
                        ],
                        ft.Text(f" → {v} veces", size=14, weight="bold")
                    ], spacing=10),
                    bgcolor="#F4F4F4",
                    padding=10,
                    border_radius=10,
                    margin=5
                ) for k, v in detectar_rotaciones(filtrado, tipo=tipo)[:10]  # top 10
            ], scroll="auto")

        ], scroll="auto")

        prediccion = ft.Column([
            ft.Text("🔮 Predicción sugerida por frecuencia", size=20, weight="bold"),
            ft.Row([
                ft.Column([
                    ft.Text(f"Posición {i+1}"),
                    ft.Image(src=COLOR_ICONOS[color], width=40)
                ]) for i, color in enumerate(pred)
            ])
        ], scroll="auto")

        # Dominancia por Estado y Turno con integración real
        dominancia_data = color_dominante_por_estado_turno(filtrado, tipo=tipo)
        dom_column = ft.Column([ft.Text("🏆 Dominancia por Estado y Turno", size=20, weight="bold")], scroll="auto")
        for (estado, draw), counter in dominancia_data.items():
            total = sum(counter.values())
            fila = ft.Row([
                ft.Image(src=STATE_ICONS[estado], width=30),
                ft.Image(src=DRAW_ICONS[draw], width=30),
                ft.Text(f"{estado}-{draw}", size=16, weight="bold")
            ])
            barras = ft.Row([
                ft.Column([
                    ft.Image(src=COLOR_ICONOS[color], width=30),
                    ft.Text(f"{(count / total) * 100:.1f}%", size=12)
                ], spacing=3) for color, count in counter.most_common()
            ], wrap=True, spacing=12)
            dom_column.controls.append(ft.Container(content=ft.Column([fila, barras]), padding=10, bgcolor="#F2F2F2", border_radius=8, margin=5))      

        # Reglas por Posición (Dominancia por posición en cada estado/turno)
        dominancia_pos = color_dominante_por_posicion_estado_turno(filtrado, tipo=tipo)

        posicion_column = ft.Column([ft.Text("📌 Reglas por Posición", size=20, weight="bold")], scroll="auto")

        for (estado, draw), lista_counters in dominancia_pos.items():
            encabezado = ft.Row([
                ft.Image(src=STATE_ICONS[estado], width=30),
                ft.Image(src=DRAW_ICONS[draw], width=30),
                ft.Text(f"{estado}-{draw}", size=16, weight="bold")
            ])

            filas_posiciones = []
            for i, counter in enumerate(lista_counters):  # Para posición 1, 2, 3
                total = sum(counter.values())
                if total == 0:
                    continue
                fila = ft.Row([
                    ft.Text(f"Posición {i+1}", size=14, weight="bold"),
                    *[
                        ft.Column([
                            ft.Image(src=COLOR_ICONOS[color], width=30),
                            ft.Text(f"{(count/total)*100:.1f}%", size=12)
                        ], spacing=3) for color, count in counter.most_common()
                    ]
                ], wrap=True, spacing=12)
                filas_posiciones.append(fila)

            posicion_column.controls.append(
                ft.Container(
                    content=ft.Column([encabezado] + filas_posiciones),
                    padding=10,
                    bgcolor="#F2F2F2",
                    border_radius=8,
                    margin=5
                )
            )


        dias_colores, repes_ciclicas = reglas_temporales_colores(filtrado, tipo=tipo)

        temporal_column = ft.Column([ft.Text("📅 Reglas Temporales", size=20, weight="bold")], scroll="auto")

        # Dominancia por día de la semana
        for dia, counter in dias_colores.items():
            total = sum(counter.values())
            if total == 0:
                continue
            fila = ft.Row([
                ft.Text(f"{dia}", size=16, weight="bold"),
                *[
                    ft.Column([
                        ft.Image(src=COLOR_ICONOS[color], width=30),
                        ft.Text(f"{(count/total)*100:.1f}%", size=12)
                    ], spacing=3) for color, count in counter.most_common()
                ]
            ], spacing=10, wrap=True)
            temporal_column.controls.append(
                ft.Container(content=fila, padding=8, bgcolor="#F0F0F0", border_radius=6, margin=4)
            )

        # Repeticiones cíclicas
        if repes_ciclicas:
            repeticiones_txt = ft.Text("🔁 Repeticiones detectadas en fechas cíclicas:", size=16, weight="bold")
            temporal_column.controls.append(ft.Divider())
            temporal_column.controls.append(repeticiones_txt)

            detalles_repes = ft.Column(scroll="auto")

            def ver_detalles_repes(dias):
                detalles = []
                for par in repes_ciclicas[dias]:
                    detalles.append(
                        ft.Container(
                            bgcolor="#EFEFEF",
                            border_radius=8,
                            padding=8,
                            margin=5,
                            content=ft.Column([
                                ft.Text(f"📅 {par['fecha1']} → {par['fecha2']}", weight="bold"),
                                ft.Row([
                                    ft.Image(src=COLOR_ICONOS[color], width=30)
                                    for color in par["colores"]
                                ])
                            ])
                        )
                    )
                detalles_repes.controls = detalles
                detalles_repes.update()

            # Botones por ciclos
            temporal_column.controls.append(
                ft.Row([
                    ft.ElevatedButton(
                        f"📍 Cada {dias} días ({len(repes_ciclicas[dias])})",
                        on_click=lambda e, d=dias: ver_detalles_repes(d)
                    )
                    for dias in repes_ciclicas
                ], wrap=True)
            )

            temporal_column.controls.append(detalles_repes)


     

        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Análisis General", content=analisis_general),
                ft.Tab(text="Reglas Detectadas", content=reglas_detectadas),
                ft.Tab(text="Predicción Sugerida", content=prediccion),
                ft.Tab(text="Dominancia Estado/Turno", content=dom_column),
                ft.Tab(text="Reglas por Posición", content=posicion_column),
                ft.Tab(text="Reglas Temporales", content=temporal_column)

            ],
            expand=True
        )

        content_column.controls = [tabs]
        page.update()

    filtro_section = ft.Column([
        ft.Text("🎯 Filtro Global", size=18, weight="bold"),
        ft.Text("✔️ Estados a incluir:"),
        ft.Row([
            ft.Column([
                ft.Image(src=STATE_ICONS[c.label], width=30, height=30),
                c
            ]) for c in check_estados
        ]),
        ft.Text("⏱️ Turnos a incluir:"),
        ft.Row([
            ft.Column([
                ft.Image(src=DRAW_ICONS[c.label], width=30, height=30),
                c
            ]) for c in check_draws
        ]),
        ft.Row([
            input_fecha_ini,
            ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: (setattr(date_ini_picker, "open", True), page.update())),
            input_fecha_fin,
            ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: (setattr(date_fin_picker, "open", True), page.update())),
        ]),
        ft.ElevatedButton("🔍 Aplicar Filtro", on_click=aplicar_filtro)
    ], visible=True)

    content_column.controls = [ft.Text("ℹ️ Aplica un filtro para comenzar el análisis")]

    actualizar_turnos()

    return ft.View(
        route="/patrones",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        ft.IconButton(icon=ft.Icons.EXPAND_MORE, on_click=lambda e: (setattr(filtro_section, "visible", not filtro_section.visible), page.update()))
                    ]),
                    filtro_section,
                    content_column
                ], expand=True),
                expand=True
            )
        ]
    )
