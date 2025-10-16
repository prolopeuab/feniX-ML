# ==========================================
# feniX-ML: Interfaz gráfica para la conversión automática de DOCX a TEI/XML
# Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde
# Grupo de investigación PROLOPE, Universitat Autònoma de Barcelona
# Descripción: Interfaz gráfica (GUI) para seleccionar archivos, validar, convertir y previsualizar
#              ediciones críticas teatrales en formato DOCX a XML-TEI.
# Este script debe utilizarse junto a tei_backend.py, visualizacion.py y main.py.
# ==========================================

# ==== IMPORTACIONES ====
import os
import sys
import tkinter as tk
import webbrowser
import ctypes
import json
from tkinter import filedialog, messagebox

# Usar CustomTkinter para esquinas redondeadas verdaderas
import customtkinter as ctk

from tei_backend import convert_docx_to_tei, validate_documents, generate_filename
from visualizacion import vista_previa_xml, vista_previa_html
from utils_icon import set_windows_icon, resource_path

# Archivo de configuración para guardar preferencias
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".fenixml_config.json")

def load_config():
    """Carga la configuración guardada."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Guarda la configuración."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

# ==== FUNCIONES DE UTILIDAD PARA MENSAJES Y AYUDA ====
def show_info(message):
    """Muestra un mensaje de ayuda en un cuadro de diálogo."""
    messagebox.showinfo("Información", message)

# ==== FUNCIÓN PRINCIPAL DE LA INTERFAZ ====
def main_gui():
    """
    Inicializa y ejecuta la interfaz gráfica principal de feniX-ML.
    Permite seleccionar archivos, validar, convertir y previsualizar resultados.
    """

    # Configuración principal de la ventana
    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("feniX-ML")
    
    # Obtener dimensiones de pantalla y calcular tamaño de ventana dinámico
    try:
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
    except:
        # Valores por defecto si falla la detección
        screen_width = 1920
        screen_height = 1080
    
    # Cargar configuración guardada
    config = load_config()
    saved_scale_mode = config.get("scale_mode", "auto")
    
    # Selector de modo de escala (compacto/amplio) integrado en el menú superior
    scale_mode_var = tk.StringVar(value=saved_scale_mode)
    def get_scale_mode():
        if scale_mode_var.get() == "auto":
            return "compacto" if (screen_width <= 1440 or screen_height <= 900) else "amplio"
        return scale_mode_var.get()

    def apply_scale():
        mode = get_scale_mode()
        print(f"[DEBUG] screen_width={screen_width}, screen_height={screen_height}, scale_mode={mode}")
        if mode == "compacto":
            # Modo compacto: para pantallas pequeñas o preferencia de interfaz compacta
            window_width = int(screen_width * 0.55)
            window_height = int(screen_height * 0.60)
            base_font = 9
            menu_font = 10
            title_font = 14
            label_font = 11
            button_font = 12
            large_button_font = 13
        else:
            # Modo amplio: para pantallas grandes, fuentes más legibles
            window_width = int(screen_width * 0.55)
            window_height = int(screen_height * 0.60)
            base_font = 11
            menu_font = 12
            title_font = 18
            label_font = 14
            button_font = 15
            large_button_font = 16
        root.geometry(f"{window_width}x{window_height}")
        root.minsize(600, 700)
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
        
        # Reiniciar la aplicación con la nueva escala
        messagebox.showinfo(
            "Cambio de escala",
            "La aplicación se reiniciará para aplicar la nueva escala."
        )
        root.destroy()
        main_gui()

    scale_mode_var.trace_add("write", on_scale_change)

    # Menú de escala integrado en el menú superior
    escala_menu = tk.Menu(root, tearoff=0, font=("Segoe UI", 10))
    escala_menu.add_radiobutton(label="Automático", variable=scale_mode_var, value="auto")
    escala_menu.add_radiobutton(label="Compacto", variable=scale_mode_var, value="compacto")
    escala_menu.add_radiobutton(label="Amplio", variable=scale_mode_var, value="amplio")
    
    # Logos con escala dinámica
    logo_scale = max(4, int(window_height / 150))
    root.logo_prolope_img = tk.PhotoImage(file=resource_path("resources/logo_prolope.png")).subsample(logo_scale, logo_scale)
    root.logo_fenix_img = tk.PhotoImage(file=resource_path("resources/logo.png")).subsample(logo_scale, logo_scale)

    # Encabezado con logo y descripción
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
    logo = tk.Label(logo_text_frame, image=root.logo_fenix_img, bg=bg_color, borderwidth=0, highlightthickness=0)
    logo.pack(anchor="w", pady=(0, 5))

    # Descripción bajo el logo
    desc = tk.Label(
        logo_text_frame,
        text="Conversor de ediciones críticas de teatro del Siglo de oro de DOCX a XML-TEI",
        font=("Segoe UI", base_font), fg="gray", wraplength=int(window_width * 0.85), bg=bg_color, justify="left"
    )
    desc.pack(anchor="w")


    # Menús de ayuda y acerca de
    def mostrar_creditos():
        messagebox.showinfo(
            "Créditos",
            "feniX-ML\nConversor de ediciones críticas en DOCX a XML-TEI\n\n"
            "Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.\n"
            "Grupo de investigación PROLOPE · Universitat Autònoma de Barcelona · 2025"
        )

    def mostrar_licencia():
        messagebox.showinfo(
            "Licencia",
            "Esta herramienta está distribuida bajo una licencia Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)."
        )

    def abrir_sitio_web():
        webbrowser.open("https://prolope.uab.cat")

    def mostrar_contacto():
        messagebox.showinfo(
            "Contacto",
            "Para consultas o sugerencias, puedes escribirnos a:\nprolope@uab.cat"
        )
    
    # Configuración del menú principal
    menubar = tk.Menu(root, font=("Segoe UI", menu_font))
    acerca_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", menu_font))
    acerca_menu.add_command(label="Créditos", command=mostrar_creditos)
    acerca_menu.add_command(label="Licencia", command=mostrar_licencia)
    acerca_menu.add_command(label="Sitio web del proyecto", command=abrir_sitio_web)
    acerca_menu.add_command(label="Contacto", command=mostrar_contacto)
    menubar.add_cascade(label="Acerca de", menu=acerca_menu)

    # Menú de escala
    menubar.add_cascade(label="Escala", menu=escala_menu)

    # Menú de ayuda
    def mostrar_ayuda_uso():
        messagebox.showinfo(
            "Cómo usar feniX-ML",
            "1. Seleccione el archivo DOCX principal (texto de la comedia).\n"
            "2. Opcionalmente, seleccione los archivos de notas, aparato y metadatos.\n"
            "3. Pulse 'Generar archivo XML-TEI' para crear el archivo de salida.\n"
            "4. Use 'Vista previa XML' o 'Vista previa HTML' para comprobar el resultado.\n\n"
            "Nota: El DOCX debe seguir los estilos predefinidos para su correcta conversión."
        )
    def abrir_instrucciones():
        webbrowser.open("https://prolopeuab.github.io/feniX-ML/") 

    def abrir_plantillas():
        webbrowser.open("https://github.com/prolopeuab/feniX-ML/tree/main/ejemplos") 

    ayuda_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", menu_font))
    ayuda_menu.add_command(label="Cómo usar feniX-ML", command=mostrar_ayuda_uso)
    ayuda_menu.add_command(label="Documentación técnica completa", command=abrir_instrucciones)
    ayuda_menu.add_command(label="Descargar plantillas DOCX", command=abrir_plantillas)
    menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
    root.config(menu=menubar)

    # Contenedor scrollable para el contenido principal
    scrollable_frame = ctk.CTkScrollableFrame(
        root, 
        fg_color="transparent",
        scrollbar_button_color="#d5d5d5",      # Gris muy claro, visible pero sutil
        scrollbar_button_hover_color="#a0a0a0" # Se oscurece al hacer hover
    )
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(5, 5))
    
    # ==== SECCIÓN 1: SELECCIÓN DE ARCHIVOS DOCX ====
    main_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=0, pady=(5, 5))
    
    frame_seleccion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_seleccion.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,8))
    
    # Título sección selección
    ctk.CTkLabel(frame_seleccion, text="Selección de archivos", 
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(12,8))

    # Selección de archivo principal
    label_main = ctk.CTkLabel(frame_seleccion, text="Prólogo y comedia:", font=("Segoe UI", label_font))
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

    # Selección de archivo de notas
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

    # Selección de archivo de aparato crítico
    label_apa = ctk.CTkLabel(frame_seleccion, text="Aparato crítico:", font=("Segoe UI", label_font))
    label_apa.grid(row=3, column=0, sticky="e", padx=(15,5), pady=5)
    entry_apa = ctk.CTkEntry(frame_seleccion, width=int(window_width * 0.5))
    entry_apa.grid(row=3, column=1, padx=5, sticky="ew")
    def select_apa():
        path = filedialog.askopenfilename(
            title="Seleccione archivo con el aparato crítico",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_apa.delete(0, tk.END)
            entry_apa.insert(0, path)
    btn_apa = ctk.CTkButton(frame_seleccion, text="Explora...", command=select_apa,
                           fg_color="#6c757d", hover_color="#5a6268",
                           corner_radius=10, width=100, height=30, font=("Segoe UI", button_font))
    btn_apa.grid(row=3, column=2, padx=(5,15), pady=5)

    # Selección de archivo de metadatos
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

    # Sección 1.5: Opciones de header TEI
    frame_header_opciones = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_header_opciones.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,8))
    
    # Variable para selección de header
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

    # ==== SECCIÓN 2: VALIDACIÓN Y VISTA PREVIA (columna izquierda) ====
    frame_output = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_output.grid(row=2, column=0, sticky="nsew", padx=(10,5), pady=(0,8))
    
    # Título sección validación
    ctk.CTkLabel(frame_output, text="Validación y vista previa",
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(12,8))

    def on_validar():
        """
        Ejecuta la validación de los archivos seleccionados y muestra los avisos encontrados.
        """
        avisos = validate_documents(
            entry_main.get(),
            notas_docx=entry_com.get() or None,
            aparato_docx=entry_apa.get() or None
        )
        if avisos:
            mensaje = (
                "⚠️ Se han encontrado las siguientes incidencias:\n\n"
                + "\n".join(avisos)
            )
        else:
            mensaje = "✅ ¡Validación completada sin incidencias!"
        messagebox.showinfo("Validación", mensaje)

    # Botones de validación y vista previa
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

    # Botón para previsualizar el XML
    btn_vista_previa_xml = ctk.CTkButton(frame_output,
        text="Vista previa (XML)",
        command=lambda: vista_previa_xml(entry_main, entry_com, entry_apa, entry_meta, root, header_mode_var.get()),
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=validation_button_height,
        font=("Segoe UI", button_font)
    )
    btn_vista_previa_xml.grid(row=2, column=0, columnspan=2, padx=15, pady=(5,5), sticky="ew")

    # Botón para previsualizar HTML
    btn_vista_previa_html = ctk.CTkButton(frame_output,
        text="Vista previa (HTML)",
        command=lambda: vista_previa_html(entry_main, entry_com, entry_apa, entry_meta, header_mode_var.get()),
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

    # ==== SECCIÓN 3: CONFIGURACIÓN DEL OUTPUT Y GUARDADO (columna derecha) ====
    frame_conversion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_conversion.grid(row=2, column=1, sticky="nsew", padx=(5,10), pady=(0,8))

    # Título sección guardar
    ctk.CTkLabel(frame_conversion, text="Guardar como",
                 font=("Segoe UI", title_font, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(12,5))
    
    # Línea informativa
    lbl_output_info = ctk.CTkLabel(frame_conversion, text="Ubicación y nombre del archivo XML de salida", 
                                   text_color="gray", font=("Segoe UI", label_font))
    lbl_output_info.grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 8))

    # Etiqueta y campo archivo de salida
    label_out = ctk.CTkLabel(frame_conversion, text="Archivo:", font=("Segoe UI", label_font))
    label_out.grid(row=2, column=0, sticky="e", padx=(15,5), pady=5)
    entry_out = ctk.CTkEntry(frame_conversion, width=int(window_width * 0.5))
    entry_out.grid(row=2, column=1, padx=5, sticky="ew")

    # Botón seleccionar archivo de salida
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

    # Botón para convertir y guardar XML-TEI
    def generate_and_save():
        # 1. Tomamos lo que haya escrito el usuario
        out = entry_out.get().strip()
        if out:
            base, ext = os.path.splitext(out)
            # Si no tenía extensión, o tenía otra, forzamos .xml
            out = base + ".xml"
        else:
            out = None

        # 2. Llamamos a la función de conversión con 'out' que ya incluye .xml
        convert_docx_to_tei(
            main_docx=entry_main.get(),
            notas_docx=entry_com.get() or None,
            aparato_docx=entry_apa.get() or None,
            metadata_docx=entry_meta.get() or None,
            output_file=out,
            save=True,
            header_mode=header_mode_var.get()
        )

        # 3. Formamos el mensaje con la ruta definitiva
        if out:
            guardado = os.path.abspath(out)
        else:
            nombre_defecto = generate_filename(entry_main.get()) + ".xml"
            guardado = os.path.abspath(nombre_defecto)

        messagebox.showinfo(
            "Conversión a XML-TEI completada",
            f"Archivo TEI generado en:\n{guardado}"
        )

    # Altura adaptable botón de conversión
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

    # ==== PIE DE PÁGINA ====
    try:
        root_bg = root.cget("background")
    except:
        root_bg = "#ffffff"
    
    # Frame horizontal para imagen y texto
    footer_frame = tk.Frame(root, bg=root_bg)
    footer_frame.pack(side="bottom", fill="x", pady=(5, 10))

    # Logo PROLOPE
    small_logo_img = root.logo_prolope_img.subsample(3, 3)
    logo_label = tk.Label(footer_frame, image=small_logo_img, bg=root_bg)
    logo_label.image = small_logo_img 
    logo_label.pack(side="left", padx=10)

    # Texto del footer (dos líneas)
    footer_text_frame = tk.Frame(footer_frame, bg=root_bg)
    footer_text_frame.pack(side="left", anchor="w")
    
    # Primera línea footer
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
    
    # Segunda línea footer
    footer_text2 = tk.Label(
        footer_text_frame,
        text="PROLOPE · Universitat Autònoma de Barcelona · 2025",
        font=("Segoe UI", footer_font_size, "bold"),
        fg="gray",
        bg=root_bg,
        justify="left",
    )
    footer_text2.pack(anchor="w")


    # Inicio del bucle principal
    root.mainloop()
