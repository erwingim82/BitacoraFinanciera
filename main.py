import flet as ft
import sqlite3
import os
import traceback
from datetime import datetime

def main(page: ft.Page):
    # Envolvemos todo en un try-except. Si falla algo crítico, lo pintará en pantalla.
    try:
        page.window_width = 380
        page.window_height = 680
        page.title = "Bitácora Financiera"
        page.theme_mode = ft.ThemeMode.DARK

        # ==========================================
        # RUTA NATIVA BLINDADA MEJORADA (ANDROID)
        # ==========================================
        try:
            if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
                # os.environ.get("HOME") es el directorio interno más seguro en Android para SQLite
                directorio_base = os.environ.get("HOME", page.get_user_data_dir())
            else:
                directorio_base = os.getcwd()
                
            os.makedirs(directorio_base, exist_ok=True)
            DB_NAME = os.path.join(directorio_base, "bitacora_financiera.db")
        except Exception as e:
            # Si falla, forzamos ruta relativa
            DB_NAME = "bitacora_financiera.db"

        def inicializar_bd():
            conexion = sqlite3.connect(DB_NAME)
            conexion.execute("PRAGMA synchronous = FULL")
            cursor = conexion.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tipo TEXT,
                                concepto TEXT,
                                monto REAL,
                                fecha TEXT
                              )''')
            conexion.commit()
            conexion.close()
            
        inicializar_bd()

        def notificar(mensaje, color=ft.colors.GREEN_700):
            page.open(ft.SnackBar(ft.Text(mensaje, color=ft.colors.WHITE), bgcolor=color, duration=3000))

        # ==========================================
        # INTERFAZ PRINCIPAL DE LA BITÁCORA
        # ==========================================
        def construir_interfaz_principal():
            page.clean()
            
            page.appbar = ft.AppBar(
                title=ft.Text("Mi Bitácora", weight=ft.FontWeight.BOLD),
                center_title=True,
                bgcolor=ft.colors.with_opacity(0.8, ft.colors.SURFACE_VARIANT),
                elevation=5
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
                    conexion = sqlite3.connect(DB_NAME)
                    cursor = conexion.cursor()
                    cursor.execute("SELECT tipo, concepto, monto, fecha FROM movimientos ORDER BY id DESC")
                    movimientos = cursor.fetchall()
                    
                    total_ingresos = 0.0
                    total_egresos = 0.0

                    for mov in movimientos:
                        tipo, concepto, monto, fecha = mov
                        
                        if tipo == "Ingreso":
                            total_ingresos += monto
                            color_monto = ft.colors.GREEN_400
                            icono = ft.icons.ARROW_UPWARD
                        else:
                            total_egresos += monto
                            color_monto = ft.colors.RED_400
                            icono = ft.icons.ARROW_DOWNWARD
                        
                        lista_movimientos.controls.append(
                            ft.ListTile(
                                leading=ft.Icon(icono, color=color_monto, size=30),
                                title=ft.Text(concepto, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(fecha),
                                trailing=ft.Text(f"${monto:.2f}", color=color_monto, weight=ft.FontWeight.BOLD, size=16),
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

                    conexion.close()
                except Exception as ex:
                    notificar(f"Error BD: {ex}", ft.colors.RED_500)
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
                    conexion = sqlite3.connect(DB_NAME)
                    cursor = conexion.cursor()
                    cursor.execute("INSERT INTO movimientos (tipo, concepto, monto, fecha) VALUES (?, ?, ?, ?)", 
                                   (drop_tipo.value, txt_concepto.value, monto_float, boton_fecha.text))
                    conexion.commit()
                    conexion.close()
                    
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

            # --- FONDO ESTABLE (STACK EN LUGAR DE BOXDECORATION) ---
            # En Android, ft.Image es mucho más seguro para assets locales
            imagen_fondo = ft.Image(
                src="Fondo.jpeg",
                fit=ft.ImageFit.COVER,
                opacity=0.2,
            )

            contenido_principal = ft.Column([
                tarjeta_balance,
                ft.Container(content=ft.Text("Historial de Movimientos", weight=ft.FontWeight.BOLD), padding=10),
                lista_movimientos
            ], expand=True)

            # Usamos un Stack para superponer el contenido sobre la imagen
            page.add(
                ft.Stack([
                    ft.Container(content=imagen_fondo, expand=True, alignment=ft.alignment.center),
                    contenido_principal
                ], expand=True)
            )
            
            cargar_datos()

        construir_interfaz_principal()

    except Exception as e:
        # ===== SISTEMA ANTI-PANTALLA NEGRA =====
        # Atrapa errores silenciosos y los dibuja en pantalla
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
