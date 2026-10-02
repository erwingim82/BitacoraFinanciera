import flet as ft
import traceback
from datetime import datetime
import urllib.parse 

def main(page: ft.Page):
    try:
        page.window_width = 380
        page.window_height = 680
        page.title = "Bitácora Financiera"
        page.theme_mode = ft.ThemeMode.DARK

        def notificar(mensaje, color=ft.colors.GREEN_700):
            page.open(ft.SnackBar(ft.Text(mensaje, color=ft.colors.WHITE), bgcolor=color, duration=3000))

        # ==========================================
        # 1. PANTALLA DE REGISTRO DE USUARIO
        # ==========================================
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
                color=ft.colors.with_opacity(0.85, ft.colors.BLUE_GREY_900),
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Bienvenido a tu Bitácora", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text("Configura tu perfil para poder exportar tus reportes.", size=14, color=ft.colors.WHITE70),
                        ft.Divider(color=ft.colors.TRANSPARENT),
                        txt_nombre,
                        txt_apellido,
                        txt_correo,
                        txt_telefono,
                        ft.FilledButton("Guardar y Entrar", on_click=guardar_usuario, style=ft.ButtonStyle(bgcolor=ft.colors.INDIGO_500), width=300)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )

            imagen_fondo = ft.Image(src="Fondo.jpeg", fit=ft.ImageFit.COVER, opacity=0.2)
            page.add(
                ft.Stack([
                    ft.Container(content=imagen_fondo, expand=True, alignment=ft.alignment.center),
                    ft.Container(content=tarjeta_registro, alignment=ft.alignment.center, padding=20)
                ], expand=True)
            )

        # ==========================================
        # 2. INTERFAZ PRINCIPAL Y EXPORTACIÓN
        # ==========================================
        def construir_interfaz_principal():
            page.clean()
            
            datos_usuario = page.client_storage.get("usuario")
            if not datos_usuario:
                return mostrar_registro()

            # --- MÓDULO DE CALCULADORA ---
            txt_pantalla_calc = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, read_only=True, border_color=ft.colors.BLUE_400, text_size=20)

            def click_calculadora(e):
                tecla = e.control.data
                if tecla == "C":
                    txt_pantalla_calc.value = "0"
                elif tecla == "=":
                    try:
                        # Evalúa la expresión matemática escrita en la pantalla
                        resultado = str(eval(txt_pantalla_calc.value))
                        txt_pantalla_calc.value = resultado
                    except Exception:
                        txt_pantalla_calc.value = "Error"
                else:
                    if txt_pantalla_calc.value == "0" or txt_pantalla_calc.value == "Error":
                        txt_pantalla_calc.value = tecla
                    else:
                        txt_pantalla_calc.value += tecla
                page.update()

            def crear_boton_calc(texto, color_fondo=ft.colors.SURFACE_VARIANT):
                return ft.ElevatedButton(
                    text=texto, data=texto, on_click=click_calculadora, 
                    style=ft.ButtonStyle(bgcolor=color_fondo, color=ft.colors.WHITE), expand=True
                )

            dialogo_calculadora = ft.AlertDialog(
                title=ft.Text("Calculadora", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=250,
                    content=ft.Column([
                        txt_pantalla_calc,
                        ft.Row([crear_boton_calc("7"), crear_boton_calc("8"), crear_boton_calc("9"), crear_boton_calc("/", ft.colors.INDIGO_500)]),
                        ft.Row([crear_boton_calc("4"), crear_boton_calc("5"), crear_boton_calc("6"), crear_boton_calc("*", ft.colors.INDIGO_500)]),
                        ft.Row([crear_boton_calc("1"), crear_boton_calc("2"), crear_boton_calc("3"), crear_boton_calc("-", ft.colors.INDIGO_500)]),
                        ft.Row([crear_boton_calc("C", ft.colors.RED_400), crear_boton_calc("0"), crear_boton_calc("="), crear_boton_calc("+", ft.colors.INDIGO_500)]),
                    ], tight=True)
                ),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_calculadora))]
            )

            # --- MÓDULO DE EXPORTACIÓN ---
            opcion_exportar = ft.Dropdown(
                label="Enviar reporte mediante:", 
                options=[ft.dropdown.Option("WhatsApp"), ft.dropdown.Option("Correo Electrónico")],
                value="WhatsApp", border_color=ft.colors.BLUE_400
            )

            def procesar_exportacion(e):
                try:
                    historial = page.client_storage.get("movimientos") or []

                    if not historial:
                        return notificar("No hay movimientos registrados para exportar.", ft.colors.ORANGE_700)

                    total_ingresos = sum([m["monto"] for m in historial if m["tipo"] == "Ingreso"])
                    total_egresos = sum([m["monto"] for m in historial if m["tipo"] == "Egreso"])
                    saldo = total_ingresos - total_egresos

                    reporte = f"📊 *REPORTE DE BITÁCORA FINANCIERA*\n\n"
                    reporte += f"👤 *Usuario:* {datos_usuario['nombre']} {datos_usuario['apellido']}\n"
                    reporte += f"💰 *Saldo Actual:* ${saldo:.2f}\n"
                    reporte += f"📈 *Total Ingresos:* ${total_ingresos:.2f}\n"
                    reporte += f"📉 *Total Egresos:* ${total_egresos:.2f}\n\n"
                    reporte += "*DETALLE DE MOVIMIENTOS:*\n"
                    
                    for mov in historial:
                        icono = "🟢" if mov["tipo"] == "Ingreso" else "🔴"
                        reporte += f"{icono} {mov['fecha']} | {mov['concepto']}: ${mov['monto']:.2f}\n"

                    reporte_codificado = urllib.parse.quote(reporte)
                    page.close(dialogo_exportar)
                    
                    if opcion_exportar.value == "WhatsApp":
                        tel_limpio = datos_usuario['telefono'].replace('+', '').replace(' ', '')
                        page.launch_url(f"https://wa.me/{tel_limpio}?text={reporte_codificado}")
                    else:
                        page.launch_url(f"mailto:{datos_usuario['correo']}?subject=Reporte de Movimientos&body={reporte_codificado}")
                        
                except Exception as ex:
                    notificar(f"Error al generar reporte: {ex}", ft.colors.RED_700)

            dialogo_exportar = ft.AlertDialog(
                title=ft.Text("Exportar Movimientos"), 
                content=ft.Column([
                    ft.Text("Genera un reporte detallado de tus finanzas."),
                    opcion_exportar
                ], tight=True), 
                actions=[
                    ft.FilledButton("Compartir", on_click=procesar_exportacion, style=ft.ButtonStyle(bgcolor=ft.colors.INDIGO_500)), 
                    ft.TextButton("Cancelar", on_click=lambda e: page.close(dialogo_exportar))
                ]
            )

            page.appbar = ft.AppBar(
                title=ft.Text(f"Bitácora de {datos_usuario['nombre']}", weight=ft.FontWeight.BOLD),
                center_title=True,
                bgcolor=ft.colors.with_opacity(0.8, ft.colors.SURFACE_VARIANT),
                elevation=5,
                actions=[
                    ft.IconButton(icon=ft.icons.CALCULATE, tooltip="Calculadora", on_click=lambda e: page.open(dialogo_calculadora)),
                    ft.IconButton(icon=ft.icons.SHARE, tooltip="Exportar Reporte", on_click=lambda e: page.open(dialogo_exportar))
                ]
            )

            lbl_saldo = ft.Text("$0.00", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
            lbl_ingresos = ft.Text("$0.00", size=16, weight=ft.FontWeight.W_500, color=ft.colors.GREEN_400)
            lbl_egresos = ft.Text("$0.00", size=16, weight=ft.FontWeight.W_500, color=ft.colors.RED_400)

            tarjeta_balance = ft.Card(
                elevation=8,
                color=ft.colors.with_opacity(0.85, ft.colors.BLUE_GREY_900),
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("SALDO ACTUAL", size=14, color=ft.colors.WHITE70),
                        lbl_saldo,
                        ft.Divider(color=ft.colors.WHITE24),
                        ft.Row([
                            ft.Column([ft.Text("Ingresos", size=12, color=ft.colors.WHITE54), lbl_ingresos]),
                            ft.Column([ft.Text("Egresos", size=12, color=ft.colors.WHITE54), lbl_egresos]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
            )

            lista_movimientos = ft.ListView(expand=True, spacing=10, padding=10)

            def cargar_datos():
                lista_movimientos.controls.clear()
                try:
                    movimientos = page.client_storage.get("movimientos") or []
                    
                    total_ingresos = 0.0
                    total_egresos = 0.0

                    for mov in reversed(movimientos):
                        if mov["tipo"] == "Ingreso":
                            total_ingresos += mov["monto"]
                            color_monto = ft.colors.GREEN_400
                            icono = ft.icons.ARROW_UPWARD
                        else:
                            total_egresos += mov["monto"]
                            color_monto = ft.colors.RED_400
                            icono = ft.icons.ARROW_DOWNWARD
                        
                        lista_movimientos.controls.append(
                            ft.ListTile(
                                leading=ft.Icon(icono, color=color_monto, size=30),
                                title=ft.Text(mov["concepto"], weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(mov["fecha"]),
                                trailing=ft.Text(f"${mov['monto']:.2f}", color=color_monto, weight=ft.FontWeight.BOLD, size=16),
                                bgcolor=ft.colors.with_opacity(0.7, ft.colors.SURFACE_VARIANT)
                            )
                        )
                    
                    saldo = total_ingresos - total_egresos
                    lbl_saldo.value = f"${saldo:.2f}"
                    lbl_ingresos.value = f"${total_ingresos:.2f}"
                    lbl_egresos.value = f"${total_egresos:.2f}"
                    
                    if saldo < 0:
                        lbl_saldo.color = ft.colors.RED_200
                    else:
                        lbl_saldo.color = ft.colors.BLUE_200

                except Exception as ex:
                    notificar(f"Error Cargando: {ex}", ft.colors.RED_500)
                page.update()

            drop_tipo = ft.Dropdown(
                label="Tipo de Registro", 
                options=[ft.dropdown.Option("Ingreso"), ft.dropdown.Option("Egreso")],
                value="Ingreso",
                border_color=ft.colors.BLUE_400
            )
            txt_concepto = ft.TextField(label="Concepto", border_color=ft.colors.BLUE_400)
            txt_monto = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.colors.BLUE_400)
            
            def cambiar_fecha(e):
                if selector_fecha.value:
                    boton_fecha.text = selector_fecha.value.strftime("%d/%m/%Y")
                    page.update()

            selector_fecha = ft.DatePicker(
                first_date=datetime(2020, 1, 1), 
                last_date=datetime(2030, 12, 31), 
                on_change=cambiar_fecha
            )
            boton_fecha = ft.OutlinedButton(
                text=datetime.now().strftime("%d/%m/%Y"), 
                icon=ft.icons.CALENDAR_MONTH, 
                on_click=lambda e: page.open(selector_fecha)
            )

            def guardar_movimiento(e):
                if not txt_concepto.value or not txt_monto.value:
                    return notificar("Completa todos los campos", ft.colors.RED_700)
                
                try:
                    monto_float = float(txt_monto.value.replace(",", "."))
                except:
                    return notificar("El monto debe ser numérico", ft.colors.RED_700)

                try:
                    movimientos = page.client_storage.get("movimientos") or []
                    movimientos.append({
                        "tipo": drop_tipo.value,
                        "concepto": txt_concepto.value,
                        "monto": monto_float,
                        "fecha": boton_fecha.text
                    })
                    page.client_storage.set("movimientos", movimientos)
                    
                    page.close(dialogo_registro)
                    notificar("Registro guardado con éxito", ft.colors.GREEN_700)
                    
                    txt_concepto.value = ""
                    txt_monto.value = ""
                    cargar_datos()
                    
                except Exception as ex:
                    notificar(f"Error al guardar: {ex}", ft.colors.RED_700)

            dialogo_registro = ft.AlertDialog(
                title=ft.Text("Nuevo Registro"), 
                content=ft.Column([
                    drop_tipo, 
                    txt_concepto, 
                    txt_monto,
                    ft.Row([ft.Text("Fecha:"), boton_fecha], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], tight=True), 
                actions=[
                    ft.FilledButton("Guardar", on_click=guardar_movimiento), 
                    ft.TextButton("Cancelar", on_click=lambda e: page.close(dialogo_registro))
                ]
            )

            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.icons.ADD, 
                bgcolor=ft.colors.INDIGO_500, 
                on_click=lambda e: page.open(dialogo_registro)
            )

            imagen_fondo = ft.Image(src="Fondo.jpeg", fit=ft.ImageFit.COVER, opacity=0.2)

            contenido_principal = ft.Column([
                tarjeta_balance,
                ft.Container(content=ft.Text("Historial de Movimientos", weight=ft.FontWeight.BOLD), padding=10),
                lista_movimientos
            ], expand=True)

            page.add(
                ft.Stack([
                    ft.Container(content=imagen_fondo, expand=True, alignment=ft.alignment.center),
                    contenido_principal
                ], expand=True)
            )
            
            cargar_datos()

        # ==========================================
        # 3. VERIFICADOR DE ARRANQUE
        # ==========================================
        if page.client_storage.contains_key("usuario"):
            construir_interfaz_principal()
        else:
            mostrar_registro()

    except Exception as e:
        error_trace = traceback.format_exc()
        page.clean()
        page.add(
            ft.ListView([
                ft.Text("Error crítico detectado", color=ft.colors.RED_ACCENT, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Mensaje: {e}", color=ft.colors.AMBER),
                ft.Text(error_trace, size=12, selectable=True)
            ], expand=True)
        )
        page.update()

ft.app(target=main)
