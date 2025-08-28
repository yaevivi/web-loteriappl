import flet as ft
import os
from datetime import datetime
from core.utils import (
    cargar_sorteos,
    obtener_loterias_ordenadas,
    filtrar_anteriores,
    obtener_historial_ultimo_dia,
    obtener_meses_y_anios,
    filtrar_por_mes_y_anio,
)
from core.predecir_fijos import predecir_fijos
from core.predecir_secuencia_peso_reverso_confiansa import predecir_por_secuencia_confianza
from core.prediccion_estado import predecir_por_secuencia_estado
from data.actualizar_sorteos_2025 import actualizar_sorteos
from views.prediccion_ia_view import prediccion_ia_view
from views.charada_view import charada_view
from views.cadena_charada_view import cadena_charada_view
from views.adivinanzas_view import adivinanzas_view
from views.adivinanza_view import adivinanza_view
from views.numero_suerte_view import numero_suerte_view
from views.coti_chiquita_view import coti_chiquita_view
from views.los_pasos_view import los_pasos_view
from views.miami_fla_view import miami_fla_view
from views.pronostico_view import pronostico_view
from views.otras_adivinanzas_view import otras_adivinanzas_view
from views.colores_view import colores_view
from views.vista_patrones import vista_patrones




def main(page: ft.Page):
    page.title = "Lotería Predictor"
    page.theme_mode = "light"
    page.window_frameless = False
    page.scroll = True
    page.bgcolor = ft.Colors.BLUE_GREY_900
    global sorteos
    sorteos = []  # inicializar
    

    def recargar_sorteos():
        global sorteos
        RUTA_JSON = os.path.join("data", "sorteos_unificados_con_fijos.json")
        try:
            sorteos = cargar_sorteos(RUTA_JSON)
            print("✅ Datos recargados desde el JSON.")
        except Exception as e:
            print(f"❌ Error recargando datos: {e}")
            sorteos = []
    

    
    try:
        recargar_sorteos()
        if not sorteos:
            raise ValueError("❌ El archivo JSON está vacío o malformado.")
    except Exception as e:
        page.add(ft.Text(f"❌ Error cargando datos: {e}", color="red"))
        return

    lista_loterias = obtener_loterias_ordenadas(sorteos)



    # Determina color de texto según el fondo

    def texto_contraste(color_fondo: str) -> str:
        claros = {
            ft.Colors.GREY_300,
            ft.Colors.GREY_100,
            ft.Colors.GREY_400,
            ft.Colors.BLUE_GREY_50,
            ft.Colors.CYAN_100,
            ft.Colors.CYAN_300,
            ft.Colors.CYAN_400
        }
        return ft.Colors.BLACK if color_fondo in claros else ft.Colors.WHITE

    # Botón personalizado con gradiente

    def crear_boton(texto, icono, color1, color2, ruta):
        texto_color = texto_contraste(color1)
        return ft.GestureDetector(
            on_tap=lambda e: page.go(ruta),
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(name=icono, size=28, color=texto_color),
                    ft.Text(texto, size=16, weight="bold", color=texto_color)
                ], alignment=ft.MainAxisAlignment.START, spacing=12),
                padding=20,
                border_radius=ft.border_radius.all(16),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=[color1, color2]
                ),
                ink=True,
                shadow=ft.BoxShadow(
                    blur_radius=6,
                    spread_radius=0,
                    color=ft.Colors.BLACK26,
                    offset=ft.Offset(0, 3),
                ),
                animate_opacity=200,
                animate_scale=200,
            ),
            on_hover=lambda e: setattr(e.control, "scale", 1.02),
        )

    # Vista principal

    def home_view():
        return ft.View(
            route="/",
            padding=0,
            controls=[
                ft.SafeArea(
                    ft.Container(
                        bgcolor=ft.Colors.BLACK,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[
                                ft.Colors.INDIGO_900,    # #1A237E
                                ft.Colors.CYAN_700,      # #00BCD4
                                ft.Colors.GREEN_400,     # #4CAF50
                                
                            ],
                        ),
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("\ud83c\udf1f Predictor de Loter\u00eda \ud83c\udf1f", size=20, weight="bold", text_align="center", color=ft.Colors.WHITE),
                                ft.Divider(color=ft.Colors.WHITE24),

                                ft.Text("\ud83d\udd2e Predicci\u00f3n", size=22, weight="bold", color=ft.Colors.BLUE_GREY_100),
                                crear_boton("Predicci\u00f3n General", "insights", ft.Colors.CYAN_400, ft.Colors.CYAN_700, "/prediccion"),
                                crear_boton("Predicci\u00f3n por Estado", "travel_explore", ft.Colors.CYAN_400, ft.Colors.CYAN_700, "/estado"),
                                crear_boton("Predicci\u00f3n IA Avanzada", "psychology", ft.Colors.CYAN_400, ft.Colors.CYAN_700, "/ia"),
                                crear_boton("Predicci\u00f3n por Colores", "color_lens", ft.Colors.CYAN_400, ft.Colors.CYAN_700, "/colores"),
                                crear_boton("Patrones por Colores", "pattern", ft.Colors.CYAN_400, ft.Colors.CYAN_700, "/patrones"),

                                ft.Divider(color=ft.Colors.WHITE24),

                                ft.Text("\ud83d\udcdc Historial", size=22, weight="bold", color=ft.Colors.BLUE_GREY_100),
                                crear_boton("Historial Hoy", "history_toggle_off", ft.Colors.GREEN_500, ft.Colors.GREEN_700, "/hoy"),
                                crear_boton("Historial por Mes", "calendar_month", ft.Colors.GREEN_500, ft.Colors.GREEN_700, "/mes"),

                                ft.Divider(color=ft.Colors.WHITE24),

                                ft.Text("\ud83c\udfb2 Extras Divertidos", size=22, weight="bold", color=ft.Colors.BLUE_GREY_100),
                                crear_boton("Adivinanzas L\u00fadicas", "extension", ft.Colors.GREY_300, ft.Colors.BLUE_GREY_50, "/adivinanzas"),
                                crear_boton("Charada Num\u00e9rica", "auto_stories", ft.Colors.GREY_300, ft.Colors.BLUE_GREY_50, "/charada"),
                                crear_boton("Cadena de Charada", "share", ft.Colors.GREY_300, ft.Colors.BLUE_GREY_50, "/cadena_charada"),

                                ft.Divider(color=ft.Colors.WHITE24),

                                crear_boton("Actualizar Datos Ahora", "cloud_sync", ft.Colors.CYAN_900, ft.Colors.CYAN_700, "/actualizar")
                            ],
                            spacing=15,
                            scroll="auto"),
                            expand=True
                        ),
                        expand=True
                    ),
                    expand=True
                )
            ]
        )




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

    def actualizar_view():
        log_output = ft.TextField(label="Resultado", multiline=True, read_only=True, min_lines=10, expand=True)
        def log(msg):
            log_output.value += msg + "\n"
            page.update()

        def ejecutar_actualizacion(e):
            log("⏳ Ejecutando actualización...")
            page.update()
            
            try:
                actualizar_sorteos(log)
            except Exception as ex:
                log(f"❌ Error: {ex}")
            
            page.update()
            recargar_sorteos()
            page.update()
    
        return ft.View(
            route="/actualizar",
            controls=[
                ft.SafeArea(
                    ft.Column([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        ft.ElevatedButton("⚙️ Ejecutar Actualización", on_click=ejecutar_actualizacion),
                        log_output
                    ], spacing=15, expand=True, scroll="auto"),
                    expand=True
                )
            ]
        )
    

    def prediccion_view():
        dropdown_objetivo = ft.Dropdown(label="Lotería Objetivo", options=[ft.dropdown.Option(l) for l in lista_loterias], expand=True)
        anteriores_checks = ft.Column(scroll="auto", expand=True)
        valores_inputs = ft.Column(scroll="auto", expand=True)
        resultado_text = ft.TextField(multiline=True, read_only=True, min_lines=10, expand=True)

        def actualizar_anteriores(e):
            anteriores_checks.controls.clear()
            valores_inputs.controls.clear()
            objetivo = dropdown_objetivo.value
            anteriores_validos = filtrar_anteriores(objetivo, lista_loterias)
            for l in anteriores_validos:
                anteriores_checks.controls.append(ft.Checkbox(label=l, value=False, on_change=actualizar_inputs))
            page.update()

        def actualizar_inputs(e):
            valores_inputs.controls.clear()
            for check in anteriores_checks.controls:
                if check.value:
                    valores_inputs.controls.append(
                        ft.TextField(label=f"Fijos de {check.label}", hint_text="Ej: 12,34,56", expand=True)
                    )
            page.update()

        def ejecutar_prediccion_secuencia(e):
            objetivo = dropdown_objetivo.value
            anteriores = [c.label for c in anteriores_checks.controls if c.value]
            valores = [v.value.replace(" ", "").split(",") for v in valores_inputs.controls]
            valores = [[f.zfill(2) for f in grupo if f] for grupo in valores]
            planos = [f for sub in valores for f in sub]

            if not objetivo or not anteriores or not planos:
                resultado_text.value = "❌ Completa todos los campos correctamente."
                page.update()
                return

            r = predecir_por_secuencia_confianza(sorteos, anteriores, planos, objetivo)
            if "error" in r:
                resultado_text.value = f"⚠️ {r['error']}"
                page.update()
                return

            resumen = [
                f"🎯 Objetivo: {r['objetivo']}",
                f"🔢 Entradas: {', '.join(r['entrada'])}",
                f"📊 Observaciones: {r['total_observaciones']}",
                "-----------------------------------",
                "Predicciones:"
            ]
            for pred in r["predicciones"]:
                resumen.append(f"🔹 Fijo: {pred['fijo']} | Frecuencia: {pred['frecuencia']} | Confianza: {pred['confianza']}%")

            resultado_text.value = "\n".join(resumen)
            page.update()

        dropdown_objetivo.on_change = actualizar_anteriores

        return ft.View(
            route="/prediccion",
            controls=[
                ft.SafeArea(
                    ft.Column([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        dropdown_objetivo,
                        ft.Text("✔️ Selecciona loterías anteriores:"),
                        anteriores_checks,
                        ft.Text("✍️ Ingresa los fijos para cada una:"),
                        valores_inputs,
                        ft.Row([
                            ft.ElevatedButton("🔍 Predecir por Secuencia", on_click=ejecutar_prediccion_secuencia),
                        ]),
                        ft.Text("📈 Resultados:", weight="bold"),
                        resultado_text
                    ], spacing=15, scroll="auto", expand=True),
                    expand=True
                )
            ]
        )

    
    def prediccion_estado_view():
        estados = sorted(set(s["state"] for s in sorteos))
        modos = [("Normal", "normal"), ("Invertida", "invertida")]
        tamanios = [2, 3, 4]

        dropdown_estado = ft.Dropdown(label="Estado de Lotería", options=[ft.dropdown.Option(e) for e in estados], expand=True)
        dropdown_draw = ft.Dropdown(label="Turno Objetivo", options=[ft.dropdown.Option(d) for d in ["M", "E", "N"]], expand=True)
        dropdown_modo = ft.Dropdown(label="Modo", options=[ft.dropdown.Option(m[1], text=m[0]) for m in modos], expand=True)
        dropdown_tamanio = ft.Dropdown(label="Tamaño de Secuencia", options=[ft.dropdown.Option(str(t)) for t in tamanios], expand=True)
        input_valores = ft.TextField(label="Valores de Secuencia (Ej: 12,34)", hint_text="Separados por comas", expand=True)
        resultado_text = ft.TextField(label="Resultados", multiline=True, read_only=True, min_lines=10, expand=True)

        def ejecutar_prediccion(e):
            estado = dropdown_estado.value
            draw = dropdown_draw.value
            modo = dropdown_modo.value
            tamanio = int(dropdown_tamanio.value or 2)
            valores = input_valores.value.replace(" ", "").split(",")

            if not estado or not draw or not modo or not valores or len(valores) < tamanio:
                resultado_text.value = "❌ Por favor, completa todos los campos correctamente."
                page.update()
                return

            r = predecir_por_secuencia_estado(sorteos, estado, draw, valores, tamanio, modo)
            if "error" in r:
                resultado_text.value = f"⚠️ {r['error']}"
                page.update()
                return

            resumen = [
                f"🎯 Estado: {r['estado']}",
                f"⏱️ Turno: {r['draw_objetivo']}",
                f"🔁 Modo: {r['modo']}",
                f"🔢 Secuencia: {', '.join(r['entrada'])}",
                f"📊 Observaciones Totales: {r['total_observaciones']}",
                "-----------------------------------",
                "Predicciones:"
            ]
            for pred in r["predicciones"]:
                resumen.append(f"🔹 Fijo: {pred['fijo']} | Frecuencia: {pred['frecuencia']} | Confianza: {pred['confianza']}%")

            resultado_text.value = "\n".join(resumen)
            page.update()

        return ft.View(
            route="/estado",
            controls=[
                ft.SafeArea(
                    ft.Column([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        dropdown_estado,
                        dropdown_draw,
                        dropdown_modo,
                        dropdown_tamanio,
                        input_valores,
                        ft.ElevatedButton("🔍 Ejecutar Predicción", on_click=ejecutar_prediccion),
                        resultado_text
                    ], spacing=15, expand=True, scroll="auto"),
                    expand=True
                )
            ]
        )


    def iconos_numericos_row(numbers_str: str) -> ft.Row:
        iconos = []
        for digito in numbers_str.strip().split("-"):
            if digito.isdigit():
                iconos.append(
                    ft.Image(
                        src=f"icons/{digito}.png",  # Ajustado a tu carpeta de íconos
                        width=32,
                        height=32,
                        fit=ft.ImageFit.CONTAIN
                    )
                )
        return ft.Row(iconos, spacing=4)

    def iconos_numericos_row_dia(numbers_str: str) -> ft.Row:
        iconos = []
        if numbers_str.isdigit():
            iconos.append(
                ft.Image(
                    src=f"icons/{numbers_str}.png",  # Ajustado a tu carpeta de íconos
                    width=32,
                    height=32,
                    fit=ft.ImageFit.CONTAIN
                )
            )
        return ft.Row(iconos, spacing=0)    

    def hoy_view():
        ultima_fecha, sorteos_dia = obtener_historial_ultimo_dia(sorteos)
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Turno")),
                ft.DataColumn(ft.Text("Premio")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Image(src=STATE_ICONS[s["state"]], width=30, height=30),),
                    ft.DataCell(ft.Image(src=DRAW_ICONS[s["draw"]], width=30, height=30),),
                    ft.DataCell(iconos_numericos_row(s["numbers"]))
                ]) for s in sorteos_dia
            ]
        )

        return ft.View(
            route="/hoy",
            controls=[
                ft.SafeArea(
                    ft.Column([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        ft.Text(f"📅 Historial del día: {ultima_fecha}", size=18, weight="bold"),
                        tabla
                    ], expand=True, scroll="auto"),
                    expand=True
                )
            ]
        )

    def mes_view():
        opciones = obtener_meses_y_anios(sorteos)
        dropdown_anio = ft.Dropdown(label="Año", options=[], expand=True)
        dropdown_mes = ft.Dropdown(label="Mes", options=[], expand=True)
        tabla = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Día")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Turno")),
            ft.DataColumn(ft.Text("Premio")),
        ], rows=[])

        for y, m in opciones:
            if str(y) not in [o.key for o in dropdown_anio.options]:
                dropdown_anio.options.append(ft.dropdown.Option(key=str(y), text=str(y)))
            mes_nombre = datetime(y, m, 1).strftime("%B").capitalize()
            if str(m) not in [o.key for o in dropdown_mes.options]:
                dropdown_mes.options.append(ft.dropdown.Option(key=str(m), text=mes_nombre))

        def actualizar(e):
            if not dropdown_anio.value or not dropdown_mes.value:
                return
            anio = int(dropdown_anio.value)
            mes = int(dropdown_mes.value)
            sorteos_filtrados = filtrar_por_mes_y_anio(sorteos, anio, mes)

            tabla.rows.clear()
            for s in sorteos_filtrados:
                tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(iconos_numericos_row_dia(s["date"][:2])),
                        ft.DataCell(ft.Image(src=STATE_ICONS[s["state"]], width=30, height=30),),
                        ft.DataCell(ft.Image(src=DRAW_ICONS[s["draw"]], width=30, height=30),),
                        ft.DataCell(iconos_numericos_row(s["numbers"]))
                    ])
                )
            page.update()

        dropdown_anio.on_change = actualizar
        dropdown_mes.on_change = actualizar

        return ft.View(
            route="/mes",
            controls=[
                ft.SafeArea(
                    ft.Column([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                        ft.Row([dropdown_anio, dropdown_mes]),
                        ft.Container(
                            content=ft.Row([tabla], scroll="auto"),
                            expand=True
                        )
                    ], expand=True, scroll="auto"),
                    expand=True
                )
            ]
        )

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view())
        elif page.route == "/prediccion":
            page.views.append(prediccion_view())
        elif page.route == "/estado":
            page.views.append(prediccion_estado_view())
        elif page.route == "/ia":
            page.views.append(prediccion_ia_view(page))
        elif page.route == "/colores":
            page.views.append(colores_view(page))
        elif page.route == "/patrones":
            page.views.append(vista_patrones(page))            
        elif page.route == "/hoy":
            page.views.append(hoy_view())
        elif page.route == "/mes":
            page.views.append(mes_view())
        elif page.route == "/adivinanzas":
            page.views.append(adivinanzas_view(page)) 
        elif page.route == "/adivinanza":
            page.views.append(adivinanza_view(page))
        elif page.route == "/pronostico":
            page.views.append(pronostico_view(page))    
        elif page.route == "/numero_suerte":
            page.views.append(numero_suerte_view(page))
        elif page.route == "/coti_chiquita":
            page.views.append(coti_chiquita_view(page))
        elif page.route == "/los_pasos":
            page.views.append(los_pasos_view(page))
        elif page.route == "/miami":
            page.views.append(miami_fla_view(page))
        elif page.route == "/otras-adivinanzas":
            page.views.append(otras_adivinanzas_view(page))               
        elif page.route == "/charada":
            page.views.append(charada_view(page))
        elif page.route == "/cadena_charada":
            page.views.append(cadena_charada_view(page))    
        elif page.route == "/actualizar":
            page.views.append(actualizar_view())    

            
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, view=ft.WEB_BROWSER, port=int(os.environ.get("PORT", 8080)))
