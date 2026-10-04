import flet as ft

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Text("¡El motor funciona perfectamente!", size=24, color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD))

ft.app(main)
