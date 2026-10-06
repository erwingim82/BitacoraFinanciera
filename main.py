import flet as ft
import traceback
from datetime import datetime
import urllib.parse 

def main(page: ft.Page):
    try:
        page.title = "Bitácora Financiera"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = ft.colors.BLACK  # Evita el destello negro inicial

        def fmt(valor):
            if valor is None: return "0,00"
            s = f"{float(valor):,.2f}"
            return s.replace(",", "X").replace(".", ",").replace("X", ".")

        def parse_float(texto):
            if not texto: return 0.0
            texto = str(texto).strip()
            if "." in texto and "," in texto:
                texto = texto.replace(".", "").replace(",", ".")
            elif "," in texto:
                texto = texto.replace(",", ".")
            return float(texto)

        def notificar(mensaje, color=ft.colors.GREEN_700):
            page.open(ft.SnackBar(ft.Text(mensaje, color=ft.colors.WHITE), bgcolor=color, duration=3000))

        def mostrar_registro():
            page.clean()
            
            txt_nombre = ft.TextField(label="Nombre", border_color=ft.colors.BLUE_400)
            txt_apellido = ft.TextField(label="Apellido", border_color=ft.colors.BLUE_400)
            txt_correo = ft.TextField(label="Correo Electrónico", keyboard_type=ft.KeyboardType.EMAIL, border_color=ft.colors.BLUE_400)
            txt_telefono = ft.TextField(label="Teléfono (Ej: +584140124578)", keyboard_type=ft.KeyboardType.PHONE, border_color=ft.colors.BLUE_400)

            def guardar_usuario(e):
                if not all([txt_nombre.value, txt_apellido.value, txt_correo.value, txt_telefono.value]):
                    return notificar("Por favor completa todos los campos", ft.colors.RED_700)
                
                try:
                    page.client_storage.set("usuario", {
                        "nombre": txt_nombre.value.strip(),
                        "apellido": txt_apellido.value.strip(),
                        "correo": txt_correo.value.strip(),
                        "telefono": txt_telefono.value.strip()
                    })
                    
                    if not page.client_storage.contains_key("movimientos"):
                        page.client_storage.set("movimientos", [])
                        
                    notificar("Perfil creado con éxito", ft.colors.GREEN_700)
                    construir_interfaz_principal()
                except Exception as ex:
                    notificar(f"Error al guardar: {ex}", ft.colors.RED_700)

            tarjeta_registro = ft.Card(
                elevation=8,
                color=ft.colors.with_opacity(0.9, ft.colors.BLUE_GREY_900),
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Bienvenido a tu Bitácora", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text("Configura tu perfil para continuar.", size=14, color=ft.colors.WHITE70),
                        ft.Divider(color=ft.colors.TRANSPARENT),
                        txt_nombre, txt_apellido, txt_correo, txt_telefono,
                        ft.FilledButton("Guardar y Entrar", on_click=guardar_usuario, style=ft.ButtonStyle(bgcolor=ft.colors.INDIGO_500), width=300)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )

            # Fondo seguro con imagen y respaldo de color sólido
            imagen_fondo = ft.Image(src="Fondo.jpeg", fit=ft.ImageFit.COVER, opacity=0.25)
            page.add(ft.Stack([ft.Container(bgcolor=ft.colors.BLACK, expand=True), ft.Container(content=imagen_fondo, expand=True, alignment=ft.alignment.center), ft.Container(content=tarjeta_registro, alignment=ft.alignment.center, padding=20)], expand=True))

        def construir_interfaz_principal():
            page.clean()
            
            saldo_usd_actual = 0.0 
            saldo_bs_actual = 0.0
            
            datos_usuario = page.client_storage.get("usuario")
            if not datos_usuario:
                return mostrar_registro()
                
            dialogo_acerca = ft.AlertDialog(
                title=ft.Text("Acerca de", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                content=ft.Column([
                    ft.Text("Bitácora Financiera", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Versión 1.4\n\nControl y registro de finanzas personales.", size=14, text_align=ft.TextAlign.CENTER),
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_acerca))]
            )

            txt_pantalla_calc = ft.TextField
