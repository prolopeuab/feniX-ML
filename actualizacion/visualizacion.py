import os
import sys
import tempfile
import webbrowser
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tei_backend import convert_docx_to_tei

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_resource(filename):
    """Carga un fichero de resources/ como texto UTF-8."""
    path = resource_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Carga los JS y CSS embebidos
CETEI_JS    = load_resource("resources/CETEIcean.js")
ESTILOS_CSS = load_resource("resources/estilos.css")

def vista_previa_xml(entry_main, entry_com, entry_apa, root):
    main_file = entry_main.get()
    com_file  = entry_com.get()
    apa_file  = entry_apa.get()

    if not main_file:
        messagebox.showerror("Error", "Seleccione al menos el DOCX Principal!")
        return

    try:
        tei_content = convert_docx_to_tei(
            main_docx=main_file,
            comentario_docx=com_file if com_file else None,
            aparato_docx=apa_file  if apa_file else None,
            output_file=None,
            save=False
        )

        preview_window = tk.Toplevel(root)
        preview_window.title("Vista previa del XML")
        preview_window.geometry("800x600")

        text_area = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, tei_content)
        text_area.configure(state='disabled')

    except Exception as e:
        messagebox.showerror("Error", f"Se ha producido un error:\n{e}")

def vista_previa_html(entry_main, entry_com, entry_apa):
    main_file = entry_main.get()
    com_file  = entry_com.get()
    apa_file  = entry_apa.get()

    if not main_file:
        messagebox.showerror("Error", "Seleccione al menos el DOCX Principal!")
        return

    try:
        tei_content = convert_docx_to_tei(
            main_docx=main_file,
            comentario_docx=com_file if com_file else None,
            aparato_docx=apa_file  if apa_file else None,
            output_file=None,
            save=False
        )

        html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Edición Digital</title>
    <style>
    {ESTILOS_CSS}
    </style>
    <script>
    {CETEI_JS}
    </script>
</head>
<body>
    <div id="tei"></div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            var ceteiInstance = new CETEI();
            var htmlNode = ceteiInstance.makeHTML5(`{tei_content}`);
            document.getElementById("tei").appendChild(htmlNode);
        }});
    </script>
</body>
</html>
"""

        tmp_file = tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8")
        tmp_file.write(html_template)
        tmp_file.close()
        webbrowser.open(f"file://{tmp_file.name}")

    except Exception as e:
        messagebox.showerror("Error", f"Se ha producido un error:\n{e}")
