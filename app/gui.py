# ==========================================
# feniX-ML: Interfaz grÃ¡fica para la conversiÃ³n automÃ¡tica de DOCX a TEI/XML
# Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde
# Grupo de investigaciÃ³n PROLOPE, Universitat AutÃ²noma de Barcelona
# DescripciÃ³n: Interfaz grÃ¡fica (GUI) para seleccionar archivos, validar, convertir y previsualizar
#              ediciones crÃ­ticas teatrales en formato DOCX a XML-TEI.
# Este script debe utilizarse junto a tei_backend.py, visualizacion.py y main.py.
# ==========================================

# --- Importaciones
import os
import sys
import tkinter as tk
import webbrowser
import ctypes
import json
import threading
import traceback
from typing import Callable, Optional, Any, cast
from tkinter import filedialog, messagebox

# Usar CustomTkinter para esquinas redondeadas verdaderas
import customtkinter as ctk

from tei_backend import convert_docx_to_tei, validate_documents, generate_filename
from visualizacion import vista_previa_xml, vista_previa_html
from utils_icon import set_windows_icon, resource_path

# Archivo de configuraciÃ³n para guardar preferencias
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".fenixml_config.json")

def load_config():
    """Carga la configuraciÃ³n guardada."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Guarda la configuraciÃ³n."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

# --- Funciones de utilidad para mensajes y ayuda
def show_info(message):
    """Muestra un mensaje de ayuda en un cuadro de diÃ¡logo."""
    messagebox.showinfo("InformaciÃ³n", message)

# --- FunciÃ³n principal de la interfaz
def main_gui():
    """
    Inicializa y ejecuta la interfaz grÃ¡fica principal de feniX-ML.
    Permite seleccionar archivos, validar, convertir y previsualizar resultados.
    """

    # ConfiguraciÃ³n principal de la ventana
    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("feniX-ML")
    
    # Obtener dimensiones de pantalla y calcular tamaÃ±o de ventana dinÃ¡mico
    try:
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
    except:
        # Valores por defecto si falla la detecciÃ³n
        screen_width = 1920
        screen_height = 1080
    
    # Cargar configuraciÃ³n guardada
    config = load_config()
    saved_scale_mode = config.get("scale_mode", "auto")
    
    # Selector de modo de escala (compacto/amplio) integrado en el menÃº superior
    scale_mode_var = tk.StringVar(value=saved_scale_mode)
    def get_scale_mode():
        if scale_mode_var.get() == "auto":
            return "compacto" if (screen_width <= 1440 or screen_height <= 900) else "amplio"
        return scale_mode_var.get()

    def apply_scale():
        mode = get_scale_mode()
        print(f"[DEBUG] screen_width={screen_width}, screen_height={screen_height}, scale_mode={mode}")
        if mode == "compacto":
            # Modo compacto
            window_width = 750
            window_height = 620
            base_font = 10
            menu_font = 11
            title_font = 15
            label_font = 12
            button_font = 13
            large_button_font = 14
        else:
            # Modo amplio
            window_width = 1050
            window_height = 620
            base_font = 11
            menu_font = 12
            title_font = 18
            label_font = 14
            button_font = 15
            large_button_font = 16
        
        # Asegurar que la ventana no exceda el tamaÃ±o de pantalla disponible
        max_width = int(screen_width * 0.95)
        max_height = int(screen_height * 0.90)
        window_width = min(window_width, max_width)
        window_height = min(window_height, max_height)
        
        root.geometry(f"{window_width}x{window_height}")
        root.minsize(700, 620)
        return base_font, menu_font, title_font, label_font, button_font, large_button_font, window_width, window_height

    # Aplicar escala inicial
    base_font, menu_font, title_font, label_font, button_font, large_button_font, window_width, window_height = apply_scale()
    root.resizable(True, True)
    set_windows_icon(root)

    def on_scale_change(*args):
        # Guardar la nueva preferencia
        new_mode = scale_mode_var.get()
        config = load_config()
        config["scale_mode"] = new_mode
        save_config(config)
        
        # Reiniciar la aplicaciÃ³n con la nueva escala
        messagebox.showinfo(
            "Cambio de escala",
            "La aplicaciÃ³n se reiniciarÃ¡ para aplicar la nueva escala."
        )
        root.destroy()
        main_gui()

    scale_mode_var.trace_add("write", on_scale_change)

    # MenÃº de escala integrado en el menÃº superior
    escala_menu = tk.Menu(root, tearoff=0, font=("Segoe UI", 10))
    escala_menu.add_radiobutton(label="AutomÃ¡tico", variable=scale_mode_var, value="auto")
    escala_menu.add_radiobutton(label="Compacto", variable=scale_mode_var, value="compacto")
    escala_menu.add_radiobutton(label="Amplio", variable=scale_mode_var, value="amplio")
    
    # Logos con escala dinÃ¡mica
    image_refs: list[tk.PhotoImage] = []
    logo_scale = max(4, int(window_height / 150))
    logo_prolope_img = tk.PhotoImage(file=resource_path("resources/logo_prolope.png")).subsample(logo_scale)
    logo_fenix_img = tk.PhotoImage(file=resource_path("resources/logo.png")).subsample(logo_scale)
    image_refs.extend([logo_prolope_img, logo_fenix_img])

    # Encabezado con logo y descripciÃ³n
    try:
        bg_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTk"]["fg_color"])
    except:
        bg_color = "#dbdbdb"
    
    header_frame = ctk.CTkFrame(root, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(10, 0))  # Reducido padding superior

    # Sub-frame para logo y texto
    logo_text_frame = tk.Frame(header_frame, bg=bg_color)
    logo_text_frame.pack(side="left", anchor="nw")

    # Logo principal
    logo = tk.Label(logo_text_frame, image=logo_fenix_img, bg=bg_color, borderwidth=0, highlightthickness=0)
    logo.pack(anchor="w", pady=(0, 5))

    # DescripciÃ³n bajo el logo
    desc = tk.Label(
        logo_text_frame,
        text="Conversor de ediciones crÃ­ticas de teatro del Siglo de oro de DOCX a XML-TEI",
        font=("Segoe UI", base_font), fg="gray", wraplength=int(window_width * 1), bg=bg_color, justify="left"
    )
    desc.pack(anchor="w")


    # MenÃºs de ayuda y acerca de
    def mostrar_creditos():
        messagebox.showinfo(
            "CrÃ©ditos",
            "feniX-ML\nConversor de ediciones crÃ­ticas en DOCX a XML-TEI\n\n"
            "Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.\n"
            "Grupo de investigaciÃ³n PROLOPE Â· Universitat AutÃ²noma de Barcelona Â· 2025"
        )

    def mostrar_licencia():
        messagebox.showinfo(
            "Licencia",
            "Esta herramienta estÃ¡ distribuida bajo una licencia Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)."
        )

    def abrir_sitio_web():
        webbrowser.open("https://prolope.uab.cat")

    def mostrar_contacto():
        messagebox.showinfo(
            "Contacto",
            "Para consultas o sugerencias, puedes escribirnos a:\nprolope@uab.cat"
        )
    
    # ConfiguraciÃ³n del menÃº principal
    menubar = tk.Menu(root, font=("Segoe UI", menu_font))
    acerca_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", menu_font))
    acerca_menu.add_command(label="CrÃ©ditos", command=mostrar_creditos)
    acerca_menu.add_command(label="Licencia", command=mostrar_licencia)
    acerca_menu.add_command(label="Sitio web del proyecto", command=abrir_sitio_web)
    acerca_menu.add_command(label="Contacto", command=mostrar_contacto)
    menubar.add_cascade(label="Acerca de", menu=acerca_menu)

    # MenÃº de escala
    menubar.add_cascade(label="Escala", menu=escala_menu)

    # MenÃº de ayuda
    def mostrar_ayuda_uso():
        messagebox.showinfo(
            "CÃ³mo usar feniX-ML",
            "1. Seleccione el archivo DOCX principal (texto de la comedia).\n"
            "2. Opcionalmente, seleccione los archivos de notas, aparato y metadatos.\n"
            "3. Pulse 'Generar archivo XML-TEI' para crear el archivo de salida.\n"
            "4. Use 'Vista previa XML' o 'Vista previa HTML' para comprobar el resultado.\n\n"
            "Nota: El DOCX debe seguir los estilos predefinidos para su correcta conversiÃ³n."
        )
    def abrir_instrucciones():
        webbrowser.open("https://prolopeuab.github.io/feniX-ML/") 

    def abrir_plantillas():
        webbrowser.open("https://github.com/prolopeuab/feniX-ML/tree/main/ejemplos") 

    ayuda_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", menu_font))
    ayuda_menu.add_command(label="CÃ³mo usar feniX-ML", command=mostrar_ayuda_uso)
    ayuda_menu.add_command(label="DocumentaciÃ³n tÃ©cnica completa", command=abrir_instrucciones)
    ayuda_menu.add_command(label="Descargar plantillas DOCX", command=abrir_plantillas)
    menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
    root.config(menu=menubar)

    # Variable para activar/desactivar el scroll
    ENABLE_SCROLL = False  # Cambia a True para activar el scroll

    if ENABLE_SCROLL:
        # Contenedor scrollable para el contenido principal
        scrollable_frame = ctk.CTkScrollableFrame(
            root, 
            fg_color="transparent",
            scrollbar_button_color="#d5d5d5",      
            scrollbar_button_hover_color="#a0a0a0" 
        )
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(5, 5))
        main_parent = scrollable_frame
    else:
        # Sin scroll, usar root directamente
        main_parent = root

    # --- SecciÃ³n 1: SelecciÃ³n de archivos DOCX
    main_frame = ctk.CTkFrame(main_parent, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=0, pady=(5, 5))
    
    frame_seleccion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_seleccion.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,8))
    
    # TÃ­tulo secciÃ³n selecciÃ³n
    ctk.CTkLabel(frame_seleccion, text="SelecciÃ³n de archivos", 
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(12,8))

    # SelecciÃ³n de archivo principal
    label_main = ctk.CTkLabel(frame_seleccion, text="PrÃ³logo y comedia:", font=("Segoe UI", label_font))
    label_main.grid(row=1, column=0, sticky="e", padx=(15,5), pady=5)
    entry_main = ctk.CTkEntry(frame_seleccion, width=int(window_width * 0.5))
    entry_main.grid(row=1, column=1, padx=5, sticky="ew")
    def select_main():
        path = filedialog.askopenfilename(
            title="Seleccione el DOCX Principal",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_main.delete(0, tk.END)
            entry_main.insert(0, path)
    btn_main = ctk.CTkButton(frame_seleccion, text="Explora...", command=select_main,
                            fg_color="#6c757d", hover_color="#5a6268",
                            corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_main.grid(row=1, column=2, padx=(5,15), pady=5)

    # SelecciÃ³n de archivo de notas
    label_com = ctk.CTkLabel(frame_seleccion, text="Notas:", font=("Segoe UI", label_font))
    label_com.grid(row=2, column=0, sticky="e", padx=(15,5), pady=5)
    entry_com = ctk.CTkEntry(frame_seleccion, width=int(window_width * 0.5))
    entry_com.grid(row=2, column=1, padx=5, sticky="ew")
    def select_com():
        path = filedialog.askopenfilename(
            title="Seleccione archivo con las notas",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_com.delete(0, tk.END)
            entry_com.insert(0, path)
    btn_com = ctk.CTkButton(frame_seleccion, text="Explora...", command=select_com,
                           fg_color="#6c757d", hover_color="#5a6268",
                           corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_com.grid(row=2, column=2, padx=(5,15), pady=5)

    # SelecciÃ³n de archivo de aparato crÃ­tico
    label_apa = ctk.CTkLabel(frame_seleccion, text="Aparato crÃ­tico:", font=("Segoe UI", label_font))
    label_apa.grid(row=3, column=0, sticky="e", padx=(15,5), pady=5)
    entry_apa = ctk.CTkEntry(frame_seleccion, width=int(window_width * 0.5))
    entry_apa.grid(row=3, column=1, padx=5, sticky="ew")
    def select_apa():
        path = filedialog.askopenfilename(
            title="Seleccione archivo con el aparato crÃ­tico",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_apa.delete(0, tk.END)
            entry_apa.insert(0, path)
    btn_apa = ctk.CTkButton(frame_seleccion, text="Explora...", command=select_apa,
                           fg_color="#6c757d", hover_color="#5a6268",
                           corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_apa.grid(row=3, column=2, padx=(5,15), pady=5)

    # SelecciÃ³n de archivo de metadatos
    ctk.CTkLabel(frame_seleccion, text="Tabla de metadatos:", font=("Segoe UI", label_font)).grid(row=4, column=0, sticky="e", padx=(15,5), pady=5)
    entry_meta = ctk.CTkEntry(frame_seleccion, width=int(window_width * 0.5))
    entry_meta.grid(row=4, column=1, padx=5, sticky="ew")
    def select_meta():
        path = filedialog.askopenfilename(
            title="Seleccione el archivo con la tabla de metadatos",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_meta.delete(0, tk.END)
            entry_meta.insert(0, path)
    btn_meta = ctk.CTkButton(frame_seleccion, text="Explora...", command=select_meta,
                            fg_color="#6c757d", hover_color="#5a6268",
                            corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_meta.grid(row=4, column=2, padx=(5,15), pady=(5,15))

    # Columna central expandible
    frame_seleccion.columnconfigure(1, weight=1)

    # SecciÃ³n 1.5: Opciones de header TEI
    frame_header_opciones = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_header_opciones.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,8))
    
    # Variable para selecciÃ³n de header
    header_mode_var = tk.StringVar(value="prolope")
    
    # Etiqueta y radio buttons
    ctk.CTkLabel(frame_header_opciones, text="Tipo de TEI-header:",
                 font=("Segoe UI", label_font, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=8)
    
    radio_prolope = ctk.CTkRadioButton(frame_header_opciones, 
                                        text="TEI-header PROLOPE",
                                        variable=header_mode_var, 
                                        value="prolope",
                                        font=("Segoe UI", label_font))
    radio_prolope.grid(row=0, column=1, sticky="w", padx=10, pady=8)
    
    radio_minimo = ctk.CTkRadioButton(frame_header_opciones, 
                                       text="TEI-header propio",
                                       variable=header_mode_var, 
                                       value="minimo",
                                       font=("Segoe UI", label_font))
    radio_minimo.grid(row=0, column=2, sticky="w", padx=10, pady=8)

    # --- SecciÃ³n 2: ValidaciÃ³n y vista previa (columna izquierda)
    frame_output = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_output.grid(row=2, column=0, sticky="nsew", padx=(10,5), pady=(0,8))
    
    # TÃ­tulo secciÃ³n validaciÃ³n
    ctk.CTkLabel(frame_output, text="ValidaciÃ³n y vista previa",
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(12,8))

    def show_validation_modal(title, message, has_warnings=False):
        """
        Muestra un modal con scroll para mensajes largos de validacion.
        """
        modal = ctk.CTkToplevel(root)
        modal.title(title)
        set_windows_icon(cast(tk.Tk, modal))
        modal.transient(root)
        modal.grab_set()

        modal_width = min(900, max(620, int(screen_width * 0.65)))
        modal_height = min(650, max(360, int(screen_height * 0.60)))
        x_pos = root.winfo_x() + max(20, (window_width - modal_width) // 2)
        y_pos = root.winfo_y() + max(20, (window_height - modal_height) // 2)
        modal.geometry(f"{modal_width}x{modal_height}+{x_pos}+{y_pos}")
        modal.minsize(520, 300)

        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(1, weight=1)

        status_text = "Se han encontrado incidencias" if has_warnings else "Validacion completada sin incidencias"
        ctk.CTkLabel(
            modal,
            text=status_text,
            font=("Segoe UI", label_font, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))

        textbox = ctk.CTkTextbox(
            modal,
            wrap="word",
            font=("Segoe UI", base_font + 1),
            activate_scrollbars=True
        )
        textbox.grid(row=1, column=0, sticky="nsew", padx=16, pady=6)
        textbox.insert("1.0", message)
        textbox.configure(state="disabled")

        ctk.CTkButton(
            modal,
            text="Cerrar",
            command=modal.destroy,
            width=110,
            corner_radius=12,
            font=("Segoe UI", button_font)
        ).grid(row=2, column=0, sticky="e", padx=16, pady=(6, 14))

        modal.bind("<Escape>", lambda _event: modal.destroy())
        modal.focus_force()

    def on_validar():
        """
        Ejecuta la validacion de los archivos seleccionados y muestra los avisos encontrados.
        """
        if not entry_main.get():
            messagebox.showwarning("Validacion", "Debe seleccionar un archivo principal.")
            return

        def do_validation():
            return validate_documents(
                entry_main.get(),
                notas_docx=entry_com.get() or None,
                aparato_docx=entry_apa.get() or None
            )

        def on_success(avisos):
            if avisos:
                mensaje = "\n\n".join(avisos)
                show_validation_modal("Validacion", mensaje, has_warnings=True)
            else:
                show_validation_modal("Validacion", "No se han detectado incidencias.", has_warnings=False)

        def on_error(e):
            messagebox.showerror("Error", f"Error durante la validacion:\n{str(e)}")

        run_with_progress(do_validation, "Validando documentos...", on_success, on_error)

    # Botones de validaciÃ³n y vista previa
    validation_button_height = max(32, int(window_height * 0.04))  

    btn_validar = ctk.CTkButton(frame_output,
        text="Validar marcado",
        command=on_validar,
        fg_color="#2b5988", 
        hover_color="#3773af",
        corner_radius=15,
        height=validation_button_height,
        font=("Segoe UI", button_font, "bold")
    )
    btn_validar.grid(row=1, column=0, columnspan=2, padx=15, pady=(5,5), sticky="ew")

    # FunciÃ³n para vista previa XML con barra de progreso
    def on_vista_previa_xml():
        if not entry_main.get():
            messagebox.showwarning("Vista previa", "Debe seleccionar un archivo principal.")
            return
        
        def do_preview():
            vista_previa_xml(entry_main, entry_com, entry_apa, entry_meta, root, header_mode_var.get())
            return None
        
        run_with_progress(do_preview, "Generando vista previa XML...")
    
    # BotÃ³n para previsualizar el XML
    btn_vista_previa_xml = ctk.CTkButton(frame_output,
        text="Vista previa (XML)",
        command=on_vista_previa_xml,
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=validation_button_height,
        font=("Segoe UI", button_font)
    )
    btn_vista_previa_xml.grid(row=2, column=0, columnspan=2, padx=15, pady=(5,5), sticky="ew")

    # FunciÃ³n para vista previa HTML con barra de progreso
    def on_vista_previa_html():
        if not entry_main.get():
            messagebox.showwarning("Vista previa", "Debe seleccionar un archivo principal.")
            return
        
        def do_preview():
            vista_previa_html(entry_main, entry_com, entry_apa, entry_meta, header_mode_var.get())
            return None
        
        run_with_progress(do_preview, "Generando vista previa HTML...")
    
    # BotÃ³n para previsualizar HTML
    btn_vista_previa_html = ctk.CTkButton(frame_output,
        text="Vista previa (HTML)",
        command=on_vista_previa_html,
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=validation_button_height,
        font=("Segoe UI", button_font)
    )
    btn_vista_previa_html.grid(row=3, column=0, columnspan=2, padx=15, pady=(5,15), sticky="ew")

    # Columnas expandibles en frame_output
    frame_output.columnconfigure(0, weight=1) 
    frame_output.columnconfigure(1, weight=1)

    # --- SecciÃ³n 3: ConfiguraciÃ³n del output y guardado (columna derecha)
    frame_conversion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_conversion.grid(row=2, column=1, sticky="nsew", padx=(5,10), pady=(0,8))

    # TÃ­tulo secciÃ³n guardar
    ctk.CTkLabel(frame_conversion, text="Guardar como",
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(12,5))
    
    # LÃ­nea informativa
    lbl_output_info = ctk.CTkLabel(frame_conversion, text="UbicaciÃ³n y nombre del archivo XML de salida", 
                                   text_color="gray", font=("Segoe UI", label_font))
    lbl_output_info.grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 8))

    # Etiqueta y campo archivo de salida
    label_out = ctk.CTkLabel(frame_conversion, text="Archivo:", font=("Segoe UI", label_font))
    label_out.grid(row=2, column=0, sticky="e", padx=(15,5), pady=5)
    entry_out = ctk.CTkEntry(frame_conversion, width=int(window_width * 0.5))
    entry_out.grid(row=2, column=1, padx=5, sticky="ew")

    # BotÃ³n seleccionar archivo de salida
    def select_out():
        result = filedialog.asksaveasfilename(
            title="Guardar archivo TEI",
            defaultextension=".xml",
            filetypes=[("Archivo XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if result:
            base, _ = os.path.splitext(result)
            path = base + ".xml"   
            entry_out.delete(0, tk.END)
            entry_out.insert(0, path)

    btn_out = ctk.CTkButton(frame_conversion, text="Explora...", command=select_out,
                           fg_color="#6c757d", hover_color="#5a6268",
                           corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_out.grid(row=2, column=2, padx=(5,15), pady=5)

    # BotÃ³n para convertir y guardar XML-TEI con barra de progreso
    def generate_and_save():
        if not entry_main.get():
            messagebox.showwarning("ConversiÃ³n", "Debe seleccionar un archivo principal.")
            return
        
        # 1. Tomamos lo que haya escrito el usuario
        out = entry_out.get().strip()
        if out:
            base, ext = os.path.splitext(out)
            out = base + ".xml"
        else:
            out = None
        
        def do_conversion():
            convert_docx_to_tei(
                main_docx=entry_main.get(),
                notas_docx=entry_com.get() or None,
                aparato_docx=entry_apa.get() or None,
                metadata_docx=entry_meta.get() or None,
                output_file=out,
                save=True,
                header_mode=header_mode_var.get()
            )
            # Retornamos la ruta del archivo guardado
            if out:
                return os.path.abspath(out)
            else:
                return os.path.abspath(generate_filename(entry_main.get()) + ".xml")
        
        def on_success(guardado):
            messagebox.showinfo("ConversiÃ³n a XML-TEI completada", f"Archivo TEI generado en:\n{guardado}")
        
        def on_error(e):
            error_details = traceback.format_exc()
            print(f"Error en conversiÃ³n:\n{error_details}")
            messagebox.showerror("Error en la conversiÃ³n", f"OcurriÃ³ un error durante la conversiÃ³n:\n{str(e)}\n\nDetalles tÃ©cnicos guardados en consola.")
        
        run_with_progress(do_conversion, "Generando archivo XML-TEI...", on_success, on_error)

    # Altura adaptable botÃ³n de conversiÃ³n
    conversion_button_height = max(36, int(window_height * 0.045))
    
    btn_convertir = ctk.CTkButton(frame_conversion,
        text="Generar archivo XML-TEI",
        command=generate_and_save,
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=conversion_button_height,
        font=("Segoe UI", button_font, "bold")
    )
    btn_convertir.grid(row=3, column=0, columnspan=3, padx=15, pady=15, sticky="ew")

    # Columna expandible en frame_conversion
    frame_conversion.columnconfigure(1, weight=1)
    
    # Grid del main_frame
    main_frame.columnconfigure(0, weight=1, uniform="cols")
    main_frame.columnconfigure(1, weight=2, uniform="cols")

    # --- Barra de progreso
    progress_frame = ctk.CTkFrame(main_parent, fg_color="transparent")
    progress_frame.pack(fill="x", padx=10, pady=(0, 5))
    
    progress_label = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", label_font))
    progress_label.pack()
    
    progress_bar = ctk.CTkProgressBar(progress_frame, width=int(window_width * 0.8), height=8)
    progress_bar.pack(pady=(5, 0))
    progress_bar.set(0)
    progress_frame.pack_forget()  # Ocultar inicialmente

    def run_with_progress(
        task_func: Callable[[], Any],
        message: str,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """
        Ejecuta una tarea en thread secundario mostrando barra de progreso indeterminada.
        
        Mantiene la GUI responsiva durante operaciones largas (conversiÃ³n, validaciÃ³n).
        Usa root.after() para actualizar UI de forma thread-safe desde el worker.
        
        Args:
            task_func: FunciÃ³n sin argumentos que ejecuta la tarea, retorna un resultado.
            message: Texto a mostrar en la barra de progreso durante ejecuciÃ³n.
            on_success: Callback(result) opcional, ejecutado en thread principal si la tarea completa.
            on_error: Callback(exception) opcional, ejecutado en thread principal si hay error.
        """
        def show_progress():
            # Mostrar barra de progreso en modo indeterminado (sin valor especÃ­fico)
            progress_frame.pack(fill="x", padx=10, pady=(0, 5), before=footer_frame)
            progress_label.configure(text=message)
            progress_bar.configure(mode="indeterminate")
            progress_bar.start()
        
        def hide_progress():
            # Detener animaciÃ³n y ocultar barra de progreso
            progress_bar.stop()
            progress_bar.configure(mode="determinate")
            progress_bar.set(0)
            progress_frame.pack_forget()
        
        def worker():
            # Ejecutar tarea en thread secundario manteniendo GUI responsiva
            try:
                # Mostrar barra de progreso en thread principal usando root.after()
                root.after(0, show_progress)
                result = task_func()
                # Ocultar barra y ejecutar callback de Ã©xito en thread principal
                root.after(0, hide_progress)
                if on_success is not None:
                    success_cb = on_success
                    root.after(0, lambda r=result, cb=success_cb: cb(r))
            except Exception as e:
                # Ocultar barra y ejecutar callback de error en thread principal
                root.after(0, hide_progress)
                if on_error is not None:
                    error_cb = on_error
                    root.after(0, lambda err=e, cb=error_cb: cb(err))
                else:
                    # Mostrar cuadro de error por defecto si no hay callback personalizado
                    root.after(0, lambda err=e: messagebox.showerror("Error", str(err)))
        
        # Iniciar thread daemon (no bloquea cierre de aplicaciÃ³n)
        threading.Thread(target=worker, daemon=True).start()

    # --- Pie de pÃ¡gina
    try:
        root_bg = root.cget("background")
    except:
        root_bg = "#ffffff"
    
    # Frame horizontal para imagen y texto
    footer_frame = tk.Frame(root, bg=root_bg)
    footer_frame.pack(side="bottom", fill="x", pady=(5, 10))

    # Logo PROLOPE
    small_logo_img = logo_prolope_img.subsample(3)
    image_refs.append(small_logo_img)
    logo_label = tk.Label(footer_frame, image=small_logo_img, bg=root_bg)
    logo_label.pack(side="left", padx=10)

    # Texto del footer (dos lÃ­neas)
    footer_text_frame = tk.Frame(footer_frame, bg=root_bg)
    footer_text_frame.pack(side="left", anchor="w")
    
    # Primera lÃ­nea footer
    footer_font_size = max(9, min(11, int(window_height / 75)))
    footer_text1 = tk.Label(
        footer_text_frame,
        text="Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde",
        font=("Segoe UI", footer_font_size),
        fg="gray",
        bg=root_bg,
        justify="left",
    )
    footer_text1.pack(anchor="w")
    
    # Segunda lÃ­nea footer
    footer_text2 = tk.Label(
        footer_text_frame,
        text="PROLOPE Â· Universitat AutÃ²noma de Barcelona Â· 2025",
        font=("Segoe UI", footer_font_size, "bold"),
        fg="gray",
        bg=root_bg,
        justify="left",
    )
    footer_text2.pack(anchor="w")


    # Inicio del bucle principal
    root.mainloop()
