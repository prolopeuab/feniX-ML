import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, scrolledtext

from tei_backend import convert_docx_to_tei, validate_documents
from visualizacion import vista_previa_xml, vista_previa_html

def show_info(message):
    """Muestra un mensaje de ayuda en un cuadro de diálogo."""
    messagebox.showinfo("Información", message)

def main_gui():
    root = tk.Tk()
    root.title("DOCXtoTEI")
    root.geometry("600x500")
    root.configure(bg="#ACBDE9")

    # Stile ttk
    style = ttk.Style(root)
    style.theme_use("clam")  # Tema "clam" per ttk
    # Imposta font e background su vari widget.
    # NB: alcuni controlli non ereditano bg facilmente, vedrai più effetto su TLabel/TFrame
    style.configure(".", font=("Open Sans", 10))  # font di default
    style.configure("TFrame", background="#ACBDE9")
    style.configure("TLabel", background="#ACBDE9")
    style.configure("TButton", font=("Open Sans", 10))

    main_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")
    main_frame.pack(fill="both", expand=True)

    # Sección 1: Selección de archivos DOCX
    frame_seleccion = ttk.Frame(main_frame, padding="10", style="TFrame", borderwidth=2, relief="ridge")
    frame_seleccion.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    # Botón info para selección de archivos
    btn_info_seleccion = ttk.Button(frame_seleccion, text="Ayuda", command=lambda: show_info("Seleccione los archivos DOCX que desea convertir a TEI."))
    btn_info_seleccion.grid(row=0, column=2, sticky="e", padx=5)


    # Título de la sección
    ttk.Label(frame_seleccion, text="Selección de archivos", font=("Open Sans", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

    # ---------- RIGA 0: DOCX Principal
    label_main = ttk.Label(frame_seleccion, text="DOCX Principal:")
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
    btn_main.grid(row=1, column=2, padx=5)

    # ---------- RIGA 1: DOCX Comentario
    label_com = ttk.Label(frame_seleccion, text="DOCX Comentario:")
    label_com.grid(row=2, column=0, sticky="e", pady=5)

    entry_com = ttk.Entry(frame_seleccion, width=60)
    entry_com.grid(row=2, column=1, padx=5, sticky="ew")

    def seleziona_com():
        path = filedialog.askopenfilename(
            title="Seleccione DOCX Comentario",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_com.delete(0, tk.END)
            entry_com.insert(0, path)

    btn_com = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_com)
    btn_com.grid(row=2, column=2, padx=5)

    # ---------- RIGA 2: DOCX Aparato
    label_apa = ttk.Label(frame_seleccion, text="DOCX Aparato:")
    label_apa.grid(row=3, column=0, sticky="e", pady=5)

    entry_apa = ttk.Entry(frame_seleccion, width=60)
    entry_apa.grid(row=3, column=1, padx=5, sticky="ew")

    def seleziona_apa():
        path = filedialog.askopenfilename(
            title="Seleccione DOCX Aparato",
            filetypes=[("Archivo DOCX", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_apa.delete(0, tk.END)
            entry_apa.insert(0, path)

    btn_apa = ttk.Button(frame_seleccion, text="Explora...", command=seleziona_apa)
    btn_apa.grid(row=3, column=2, padx=5)

    # Hace que la columna central (entries) sea expandible
    frame_seleccion.columnconfigure(1, weight=1)


    # Sección 2: Validación y vista previa
    frame_output = ttk.Frame(main_frame, padding="10", style="TFrame", borderwidth=2, relief="ridge")
    frame_output.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

    # Título de la sección
    ttk.Label(frame_output, text="Validación y vista previa", font=("Open Sans", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

    def on_validar():
        avisos = validate_documents(
            entry_main.get(),
            comentario_docx=entry_com.get() or None,
            aparato_docx=entry_apa.get() or None
        )
        mensaje = "\n".join(avisos) if avisos else "Sin warnings."
        messagebox.showinfo("Validación", mensaje)

    # Botón para validar el marcado
    btn_validar = ttk.Button(frame_output,
        text="Validar marcado",
        command=on_validar
    )
    btn_validar.grid(row=1, column=0, rowspan=2, padx=5, pady=10, sticky="nsew")  

    # Botón de vista previa XML
    btn_vista_previa_xml = ttk.Button(frame_output,
        text="Vista previa (XML)",
        command=lambda: vista_previa_xml(entry_main, entry_com, entry_apa, root)
    )
    btn_vista_previa_xml.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Botón de vista previa Edición Digital HTML
    btn_vista_previa_html = ttk.Button(frame_output,
        text="Vista previa (HTML)",
        command=lambda: vista_previa_html(entry_main, entry_com, entry_apa)
    )
    btn_vista_previa_html.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Ajustar las columnas y filas para que los botones se distribuyan correctamente
    frame_output.columnconfigure(0, weight=1) 
    frame_output.columnconfigure(1, weight=2) 
    frame_output.rowconfigure(1, weight=1) 
    frame_output.rowconfigure(2, weight=1)

    # Sección 3: Configuración del output y guardar
    frame_conversion = ttk.Frame(main_frame, padding="10", style="TFrame", borderwidth=2, relief="ridge")
    frame_conversion.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    # Título de la sección
    ttk.Label(frame_conversion, text="Configuración del output", font=("Open Sans", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

    # Campo para seleccionar el archivo de salida
    label_out = ttk.Label(frame_conversion, text="Output XML:")
    label_out.grid(row=1, column=0, sticky="e", pady=5)

    entry_out = ttk.Entry(frame_conversion, width=60)
    entry_out.grid(row=1, column=1, padx=5, sticky="ew")

    def seleziona_out():
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("Archivo XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if path:
            entry_out.delete(0, tk.END)
            entry_out.insert(0, path)

    btn_out = ttk.Button(frame_conversion, text="Guardar como...", command=seleziona_out)
    btn_out.grid(row=1, column=2, padx=5)

    # Botón Convertir
    btn_convertir = ttk.Button(frame_conversion,
        text="Convertir a TEI",
        command=lambda: (
            convert_docx_to_tei(
                main_docx=entry_main.get(),
                comentario_docx=entry_com.get() or None,
                aparato_docx=entry_apa.get() or None,
                output_file=entry_out.get() or None,
                save=True
            ),
            messagebox.showinfo(
                "Operación completada",
                f"Archivo TEI generado en:\n{entry_out.get() or generate_filename(entry_main.get()) + '.xml'}"
            )
        )
    )
    btn_convertir.grid(row=2, column=2, padx=5, pady=5, sticky="ew")



    # Ajuste para expandir el campo de texto correctamente
    frame_conversion.columnconfigure(1, weight=1)


    # Hace que la columna 0 se expanda
    main_frame.columnconfigure(0, weight=1)

    root.mainloop()
