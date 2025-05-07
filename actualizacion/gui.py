import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from tkinter import filedialog, messagebox
from tkinter import ttk

from tei_backend import convert_docx_to_tei, validate_documents, generate_filename
from visualizacion import vista_previa_xml, vista_previa_html

def show_info(message):
    """Muestra un mensaje de ayuda en un cuadro de diálogo."""
    messagebox.showinfo("Información", message)

def main_gui():
    root = tk.Tk()
    root.title("feniX-ML")
    root.geometry("1000x800")
    root.configure(bg="#F0F2F5")

    # 🎨 Estilos modernos con ttk
    style = ttk.Style(root)
    style.theme_use("clam")  

    # Tipografía general
    style.configure(".", font=("Segoe UI", 10))

    # Fondo claro coherente con toda la interfaz
    style.configure("TFrame", background="#F0F2F5")
    style.configure("TLabel", background="#F0F2F5")
    style.configure("TLabelframe", background="#F0F2F5")
    style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), background="#F0F2F5", foreground="#1A1A1A")

    # Estilo de botones modernos
    style.configure("TButton",
        font=("Segoe UI", 10),
        padding=6,
        relief="flat",
        background="#142a40",  
        foreground="white"
    )
    style.map("TButton",
        background=[("active", "#357ABD")],
        relief=[("pressed", "sunken")]
    )

    

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
    
    # Menú "Acerca de"
    acerca_menu = tk.Menu(menubar := tk.Menu(root), tearoff=0)
    acerca_menu.add_command(label="Créditos", command=mostrar_creditos)
    acerca_menu.add_command(label="Licencia", command=mostrar_licencia)
    acerca_menu.add_command(label="Sitio web del proyecto", command=abrir_sitio_web)
    acerca_menu.add_command(label="Contacto", command=mostrar_contacto)
    menubar.add_cascade(label="Acerca de", menu=acerca_menu)

    def mostrar_ayuda_uso():
        messagebox.showinfo(
            "Cómo usar feniX-ML",
            "1. Seleccione el archivo DOCX principal (texto de la comedia).\n"
            "2. Opcionalmente, seleccione los archivos de comentario, aparato y metadatos.\n"
            "3. Pulse 'Generar archivo XML-TEI' para crear el archivo de salida.\n"
            "4. Use 'Vista previa XML' o 'Vista previa HTML' para comprobar el resultado.\n\n"
            "Nota: El DOCX debe seguir los estilos predefinidos para su correcta conversión."
        )
    def abrir_instrucciones():
        webbrowser.open("https://tusitio.com/fenixml/instrucciones")  # ← reemplaza con tu enlace real

    def abrir_plantillas():
        webbrowser.open("https://tusitio.com/fenixml/plantillas")  # ← reemplaza con tu enlace real

    # Menú "Ayuda"
    ayuda_menu = tk.Menu(menubar, tearoff=0)
    ayuda_menu.add_command(label="Cómo usar feniX-ML", command=mostrar_ayuda_uso)
    ayuda_menu.add_command(label="Documentación técnica completa", command=abrir_instrucciones)
    ayuda_menu.add_command(label="Descargar plantillas DOCX", command=abrir_plantillas)
    menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

    root.config(menu=menubar)

    main_frame = ttk.Frame(root, padding="10", style="TFrame")
    main_frame.pack(fill="both", expand=True)



    # Sección 1: Selección de archivos DOCX
    frame_seleccion = ttk.LabelFrame(main_frame, text="Selección de archivos", padding="10", style="TLabelframe")
    frame_seleccion.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)



    # ---------- RIGA 0: DOCX Principal
    label_main = ttk.Label(frame_seleccion, text="Prólogo y comedia:")
    label_main.grid(row=1, column=0, sticky="e", pady=5)

    entry_main = ttk.Entry(frame_seleccion, width=60)
    entry_main.grid(row=1, column=1, padx=5, sticky="ew")

    def seleziona_main():
        path = filedialog.askopenfilename(
            title="Seleccione el DOCX Principal",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_main.delete(0, tk.END)
            entry_main.insert(0, path)

    btn_main = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_main)
    btn_main.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    # ---------- RIGA 1: DOCX Comentario
    label_com = ttk.Label(frame_seleccion, text="Notas filológicas:")
    label_com.grid(row=2, column=0, sticky="e", pady=5)

    entry_com = ttk.Entry(frame_seleccion, width=60)
    entry_com.grid(row=2, column=1, padx=5, sticky="ew")

    def seleziona_com():
        path = filedialog.askopenfilename(
            title="Seleccione archivo con las notas filológicas",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_com.delete(0, tk.END)
            entry_com.insert(0, path)

    btn_com = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_com)
    btn_com.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    # ---------- RIGA 2: DOCX Aparato
    label_apa = ttk.Label(frame_seleccion, text="Aparato crítico:")
    label_apa.grid(row=3, column=0, sticky="e", pady=5)

    entry_apa = ttk.Entry(frame_seleccion, width=60)
    entry_apa.grid(row=3, column=1, padx=5, sticky="ew")

    def seleziona_apa():
        path = filedialog.askopenfilename(
            title="Seleccione archivo con el aparato crítico",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_apa.delete(0, tk.END)
            entry_apa.insert(0, path)

    btn_apa = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_apa)
    btn_apa.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

    # ---------- RIGA 3: Archivo de Metadatos
    ttk.Label(frame_seleccion, text="Tabla de metadatos:").grid(row=4, column=0, sticky="e", pady=5)
    entry_meta = ttk.Entry(frame_seleccion, width=60)
    entry_meta.grid(row=4, column=1, padx=5, sticky="ew")
    def seleziona_meta():
        path = filedialog.askopenfilename(
            title="Seleccione el archivo con la tabla de metadatos",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_meta.delete(0, tk.END)
            entry_meta.insert(0, path)
    btn_meta = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_meta)
    btn_meta.grid(row=4, column=2, padx=5, pady=5, sticky="ew")


    # Hace que la columna central (entries) sea expandible
    frame_seleccion.columnconfigure(1, weight=1)


    # Sección 2: Validación y vista previa
    frame_output = ttk.LabelFrame(main_frame, text="Validación y vista previa", padding="10", style="TLabelframe")
    frame_output.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    def on_validar():
        avisos = validate_documents(
            entry_main.get(),
            comentario_docx=entry_com.get() or None,
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


    # Botón para validar el marcado
    btn_validar = ttk.Button(frame_output,
        text="✔ Validar marcado",
        command=on_validar
    )
    btn_validar.grid(row=1, column=0, rowspan=2, padx=10, pady=5, sticky="nsew")

    # Botón de vista previa XML
    btn_vista_previa_xml = ttk.Button(frame_output,
        text="🗎 Vista previa (XML)",
        command=lambda: vista_previa_xml(entry_main, entry_com, entry_apa, entry_meta, root)
    )
    btn_vista_previa_xml.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Botón de vista previa Edición Digital HTML
    btn_vista_previa_html = ttk.Button(frame_output,
        text="🌐 Vista previa (HTML)",
        command=lambda: vista_previa_html(entry_main, entry_com, entry_apa, entry_meta)
    )
    btn_vista_previa_html.grid(row=2, column=1, padx=5, pady=5, sticky="ew")


    # Ajustar las columnas y filas para que los botones se distribuyan correctamente
    frame_output.columnconfigure(0, weight=1) 
    frame_output.columnconfigure(1, weight=2) 
    frame_output.rowconfigure(1, weight=1) 
    frame_output.rowconfigure(2, weight=1)

    # Sección 3: Configuración del output y guardar
    frame_conversion = ttk.LabelFrame(main_frame, text="Guardar como", padding="10", style="TLabelframe")
    frame_conversion.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    # Línea informativa en gris
    lbl_output_info = ttk.Label(frame_conversion, text="Ubicación y nombre del archivo XML de salida", foreground="gray")
    lbl_output_info.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

    # Etiqueta y campo para archivo
    label_out = ttk.Label(frame_conversion, text="Archivo:")
    label_out.grid(row=1, column=0, sticky="e", pady=5)

    entry_out = ttk.Entry(frame_conversion, width=60)
    entry_out.grid(row=1, column=1, padx=5, sticky="ew")

    # Botón para seleccionar archivo de salida
    def seleziona_out():
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("Archivo XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_out.delete(0, tk.END)
            entry_out.insert(0, path)

    btn_out = ttk.Button(frame_conversion, text="Explora...", command=seleziona_out)
    btn_out.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    # Botón Convertir
    btn_convertir = ttk.Button(frame_conversion,
        text="⚙️ Generar archivo XML-TEI",
        command=lambda: (
            convert_docx_to_tei(
                main_docx=entry_main.get(),
                comentario_docx=entry_com.get() or None,
                aparato_docx=entry_apa.get() or None,
                metadata_docx=entry_meta.get() or None,
                output_file=entry_out.get() or None,
                save=True
            ),
            messagebox.showinfo(
                "Conversión a XML-TEI completada",
                f"Archivo TEI generado en:\n{entry_out.get() or generate_filename(entry_main.get()) + '.xml'}"
            )
        )
    )
    btn_convertir.grid(row=2, column=0, columnspan=3, padx=10, pady=15, sticky="ew")


    # Ajuste para expandir el campo de texto correctamente
    frame_conversion.columnconfigure(1, weight=1)


    # Hace que la columna 0 se expanda
    main_frame.columnconfigure(0, weight=1)

    footer = tk.Label(
        root,
        text="Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde\nPROLOPE · Universitat Autònoma de Barcelona · 2025",
        font=("Segoe UI", 10),
        fg="gray",
        bg=root.cget("bg"),
        justify="center",
    )
    footer.pack(side="bottom", fill="x", pady=10)



    root.mainloop()
