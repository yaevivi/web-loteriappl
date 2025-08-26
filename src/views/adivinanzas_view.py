import flet as ft


def adivinanzas_view(page: ft.Page):
    def ir_a(ruta):
        page.go(ruta)

    return ft.View(
        route="/adivinanzas",
        controls=[
            ft.SafeArea(
                ft.Column([
                    ft.ElevatedButton("⬅️ Volver", on_click=lambda e: page.go("/")),
                    ft.Text("🔮 Adivinanzas y funciones especiales", size=20, weight="bold"),
                    ft.ElevatedButton("📜 Adivinanza", on_click=lambda e: ir_a("/adivinanza")),
                    ft.ElevatedButton("🔥 Pronostico", on_click=lambda e: ir_a("/pronostico")),
                    ft.ElevatedButton("🍀 Número de la Suerte", on_click=lambda e: ir_a("/numero_suerte")),
                    ft.ElevatedButton("🧒 La Coti Chiquita", on_click=lambda e: ir_a("/coti_chiquita")),
                    ft.ElevatedButton("👣 Los Pasos", on_click=lambda e: ir_a("/los_pasos")),
                    ft.ElevatedButton("🌴 Miami Fla", on_click=lambda e: ir_a("/miami")),
                    ft.ElevatedButton("💫 Otras adivinanzas", on_click=lambda e: ir_a("/otras-adivinanzas"))

                ], spacing=15, expand=True, scroll="auto"),
                expand=True
            )
        ]
    )
