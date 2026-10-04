import flet as ft
import traceback

def main(page: ft.Page):
    page.title = "Diagnóstico Bitácora"
    page.theme_mode = ft.ThemeMode.DARK
    
    try:
        # Intentamos verificar si client_storage responde en Android
        test_val = page.client_storage.get("usuario")
        
        page.add(
            ft.Column([
                ft.Text("¡Flet está vivo en Android!", size=20, color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD),
                ft.Text(f"Estado de almacenamiento: {'OK'}", size=14),
                ft.ElevatedButton("Probar avanzar", on_click=lambda e: print("Click OK"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        page.clean()
        page.add(
            ft.ListView([
                ft.Text("Fallo Crítico al Iniciar:", color=ft.colors.RED_ACCENT, size=18, weight=ft.FontWeight.BOLD),
                ft.Text(str(e), color=ft.colors.YELLOW, size=14),
                ft.Text(error_trace, size=10, selectable=True, color=ft.colors.WHITE70)
            ], expand=True, padding=20)
        )
    page.update()

ft.app(target=main)
