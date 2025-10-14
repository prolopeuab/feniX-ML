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
from tkinter import filedialog, messagebox

# Usar CustomTkinter para esquinas redondeadas verdaderas
import customtkinter as ctk

from tei_backend import convert_docx_to_tei, validate_documents, generate_filename
from visualizacion import vista_previa_xml, vista_previa_html

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        # Si está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Si se ejecuta como script, usar el directorio del archivo actual
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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

    # --- Configuración de la ventana principal con CustomTkinter ---
    ctk.set_appearance_mode("light")  # Modo claro
    ctk.set_default_color_theme("blue")  # Tema base (lo personalizaremos)
    
    root = ctk.CTk()
    root.title("feniX-ML")
    root.geometry("1000x920")

    # Icono de la ventana
    try:
        root.iconbitmap(resource_path("resources/icon.ico"))
    except Exception:
        pass  # Si no se encuentra el icono, usa el predeterminado
    
    # Cargar logos
    root.logo_prolope_img = tk.PhotoImage(file=resource_path("resources/logo_prolope.png")).subsample(6, 6)
    root.logo_fenix_img = tk.PhotoImage(file=resource_path("resources/logo.png")).subsample(4, 4)  # Más pequeño

    # ==== ENCABEZADO CON LOGO Y DESCRIPCIÓN ====
    # Obtener color de fondo
    try:
        bg_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTk"]["fg_color"])
    except:
        bg_color = "#dbdbdb"
    
    header_frame = ctk.CTkFrame(root, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(15, 10))

    header_frame.grid_columnconfigure(1, weight=1)  # la columna del texto se expande

    # Logo
    logo = tk.Label(header_frame, image=root.logo_fenix_img, bg=bg_color, borderwidth=0, highlightthickness=0)
    logo.grid(row=0, column=0, sticky="sw", padx=(0, 15), pady=5)

    # Texto
    desc = tk.Label(
        header_frame,
        text="Conversor de ediciones críticas de teatro del Siglo de oro de DOCX a XML-TEI",
        font=("Segoe UI", 9), fg="gray", wraplength=600, bg=bg_color, justify="left"
    )
    desc.grid(row=0, column=1, sticky="sw", pady=5)


    # ==== MENÚS DE AYUDA Y ACERCA DE ====
    # Menú "Acerca de" con créditos, licencia, web y contacto
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
    acerca_menu = tk.Menu(menubar := tk.Menu(root), tearoff=0)
    acerca_menu.add_command(label="Créditos", command=mostrar_creditos)
    acerca_menu.add_command(label="Licencia", command=mostrar_licencia)
    acerca_menu.add_command(label="Sitio web del proyecto", command=abrir_sitio_web)
    acerca_menu.add_command(label="Contacto", command=mostrar_contacto)
    menubar.add_cascade(label="Acerca de", menu=acerca_menu)

    # Menú "Ayuda" con instrucciones y plantillas
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

    ayuda_menu = tk.Menu(menubar, tearoff=0)
    ayuda_menu.add_command(label="Cómo usar feniX-ML", command=mostrar_ayuda_uso)
    ayuda_menu.add_command(label="Documentación técnica completa", command=abrir_instrucciones)
    ayuda_menu.add_command(label="Descargar plantillas DOCX", command=abrir_plantillas)
    menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
    root.config(menu=menubar)

    # ==== SECCIÓN 1: SELECCIÓN DE ARCHIVOS DOCX ====
    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
    
    frame_seleccion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_seleccion.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
    
    # Título de la sección
    ctk.CTkLabel(frame_seleccion, text="Selección de archivos", 
                 font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15,10))

    # --- Selección de archivo principal (prólogo y comedia) ---
    label_main = ctk.CTkLabel(frame_seleccion, text="Prólogo y comedia:", font=("Segoe UI", 14))
    label_main.grid(row=1, column=0, sticky="e", padx=(15,5), pady=5)
    entry_main = ctk.CTkEntry(frame_seleccion, width=400)
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
                            corner_radius=10, width=100, height=30, font=("Segoe UI", 14))
    btn_main.grid(row=1, column=2, padx=(5,15), pady=5)

    # --- Selección de archivo de notas ---
    label_com = ctk.CTkLabel(frame_seleccion, text="Notas:", font=("Segoe UI", 14))
    label_com.grid(row=2, column=0, sticky="e", padx=(15,5), pady=5)
    entry_com = ctk.CTkEntry(frame_seleccion, width=400)
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
                           corner_radius=10, width=100, height=30, font=("Segoe UI", 14))
    btn_com.grid(row=2, column=2, padx=(5,15), pady=5)

    # --- Selección de archivo de aparato crítico ---
    label_apa = ctk.CTkLabel(frame_seleccion, text="Aparato crítico:", font=("Segoe UI", 14))
    label_apa.grid(row=3, column=0, sticky="e", padx=(15,5), pady=5)
    entry_apa = ctk.CTkEntry(frame_seleccion, width=400)
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
                           corner_radius=10, width=100, height=30, font=("Segoe UI", 14))
    btn_apa.grid(row=3, column=2, padx=(5,15), pady=5)

    # --- Selección de archivo de metadatos ---
    ctk.CTkLabel(frame_seleccion, text="Tabla de metadatos:", font=("Segoe UI", 14)).grid(row=4, column=0, sticky="e", padx=(15,5), pady=5)
    entry_meta = ctk.CTkEntry(frame_seleccion, width=400)
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
                            corner_radius=10, width=100, height=30, font=("Segoe UI", 14))
    btn_meta.grid(row=4, column=2, padx=(5,15), pady=(5,15))

    # Hace que la columna central (entries) sea expandible
    frame_seleccion.columnconfigure(1, weight=1)

    # ==== SECCIÓN 2: VALIDACIÓN Y VISTA PREVIA ====
    frame_output = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_output.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
    
    # Título de la sección
    ctk.CTkLabel(frame_output, text="Validación y vista previa",
                 font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15,10))

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

    # Botón para validar el marcado con esquinas redondeadas (CustomTkinter)
    btn_validar = ctk.CTkButton(frame_output,
        text="✔ Validar marcado",
        command=on_validar,
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        width=180,
        height=70,
        font=("Segoe UI", 18, "bold")
    )
    btn_validar.grid(row=1, column=0, rowspan=2, padx=15, pady=(5,15), sticky="nsew")

    # Botón para previsualizar el XML con esquinas redondeadas
    btn_vista_previa_xml = ctk.CTkButton(frame_output,
        text="🗎 Vista previa (XML)",
        command=lambda: vista_previa_xml(entry_main, entry_com, entry_apa, entry_meta, root),
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=50,
        font=("Segoe UI", 18)
    )
    btn_vista_previa_xml.grid(row=1, column=1, padx=(5,15), pady=(5,5), sticky="ew")

    # Botón para previsualizar HTML con esquinas redondeadas
    btn_vista_previa_html = ctk.CTkButton(frame_output,
        text="🌐 Vista previa (HTML)",
        command=lambda: vista_previa_html(entry_main, entry_com, entry_apa, entry_meta),
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=50,
        font=("Segoe UI", 18)
    )
    btn_vista_previa_html.grid(row=2, column=1, padx=(5,15), pady=(5,15), sticky="ew")

    # Ajustar las columnas y filas para que los botones se distribuyan correctamente
    frame_output.columnconfigure(0, weight=1) 
    frame_output.columnconfigure(1, weight=2) 
    frame_output.rowconfigure(1, weight=1) 
    frame_output.rowconfigure(2, weight=1)

    # ==== SECCIÓN 3: CONFIGURACIÓN DEL OUTPUT Y GUARDADO ====
    frame_conversion = ctk.CTkFrame(main_frame, corner_radius=10)
    frame_conversion.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    # Título de la sección
    ctk.CTkLabel(frame_conversion, text="Guardar como",
                 font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15,5))
    
    # Línea informativa en gris
    lbl_output_info = ctk.CTkLabel(frame_conversion, text="Ubicación y nombre del archivo XML de salida", 
                                   text_color="gray", font=("Segoe UI", 14))
    lbl_output_info.grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 10))

    # Etiqueta y campo para archivo de salida
    label_out = ctk.CTkLabel(frame_conversion, text="Archivo:", font=("Segoe UI", 14))
    label_out.grid(row=2, column=0, sticky="e", padx=(15,5), pady=5)
    entry_out = ctk.CTkEntry(frame_conversion, width=400)
    entry_out.grid(row=2, column=1, padx=5, sticky="ew")

    # Botón para seleccionar archivo de salida
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
                           corner_radius=10, width=100, height=30, font=("Segoe UI", 14))
    btn_out.grid(row=2, column=2, padx=(5,15), pady=5)

    # Botón para convertir y guardar el archivo XML-TEI
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
            save=True
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

    btn_convertir = ctk.CTkButton(frame_conversion,
        text="⚙️ Generar archivo XML-TEI",
        command=generate_and_save,
        fg_color="#142a40",
        hover_color="#1a3650",
        corner_radius=15,
        height=50,
        font=("Segoe UI", 18, "bold")
    )
    btn_convertir.grid(row=3, column=0, columnspan=3, padx=15, pady=15, sticky="ew")

    # Ajuste para expandir el campo de texto correctamente
    frame_conversion.columnconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)

    # ==== PIE DE PÁGINA ====
    # Obtener color de fondo de forma segura
    try:
        root_bg = root.cget("background")
    except:
        root_bg = "#ffffff"
    
    # Frame para agrupar imagen y texto en horizontal
    footer_frame = tk.Frame(root, bg=root_bg)
    footer_frame.pack(side="bottom", fill="x", pady=(5, 10))

    # Imagen del logo de PROLOPE (izquierda)
    logo_label = tk.Label(footer_frame, image=root.logo_prolope_img, bg=root_bg)
    logo_label.pack(side="left", padx=10)

    # Texto del footer (derecha) - contenedor vertical para dos líneas
    footer_text_frame = tk.Frame(footer_frame, bg=root_bg)
    footer_text_frame.pack(side="left", anchor="w")
    
    # Primera línea: texto normal
    footer_text1 = tk.Label(
        footer_text_frame,
        text="Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde",
        font=("Segoe UI", 10),
        fg="gray",
        bg=root_bg,
        justify="left",
    )
    footer_text1.pack(anchor="w")
    
    # Segunda línea: texto en negrita
    footer_text2 = tk.Label(
        footer_text_frame,
        text="PROLOPE · Universitat Autònoma de Barcelona · 2025",
        font=("Segoe UI", 10, "bold"),
        fg="gray",
        bg=root_bg,
        justify="left",
    )
    footer_text2.pack(anchor="w")


    # ==== INICIO DEL BUCLE PRINCIPAL ====
    root.mainloop()
