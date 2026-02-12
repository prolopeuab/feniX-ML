# ==========================================
# feniX-ML: Visualización y previsualización de TEI/XML
# Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde
# Grupo de investigación PROLOPE, Universitat Autònoma de Barcelona
# Descripción: Utilidades para mostrar y previsualizar el resultado de la conversión
#              de textos teatrales DOCX a TEI/XML, tanto en formato XML como HTML.
# Este script debe utilizarse junto a tei_backend.py, gui.py y main.py.
# ==========================================

# ==== IMPORTACIONES ====
import os
import sys
import tempfile
import webbrowser
import traceback
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tei_backend import convert_docx_to_tei

# ==== UTILIDADES DE RECURSOS ====
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        # Si está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Si se ejecuta como script, usar el directorio del archivo actual
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_resource(filename):
    """Carga un fichero de resources/ como texto UTF-8."""
    path = resource_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ==== CARGA DE RECURSOS ESTÁTICOS (JS y CSS) ====
CETEI_JS    = load_resource("resources/CETEIcean.js")
ESTILOS_CSS = load_resource("resources/estilos.css")

# ==== VISTAS DE PREVISUALIZACIÓN ====
def vista_previa_xml(entry_main, entry_com, entry_apa, entry_meta, root, header_mode="prolope"):
    """
    Muestra una ventana con la previsualización del XML TEI generado.
    """
    main_file = entry_main.get()
    com_file  = entry_com.get()
    apa_file  = entry_apa.get()

    if not main_file:
        messagebox.showerror("Error", "Seleccione al menos el DOCX que contiene el prólogo y la comedia.")
        return

    try:
        tei_content = convert_docx_to_tei(
            main_docx=main_file,
            notas_docx=com_file if com_file else None,
            aparato_docx=apa_file  if apa_file else None,
            metadata_docx=entry_meta.get() or None,
            output_file=None,
            save=False,
            header_mode=header_mode
        )


        preview_window = tk.Toplevel(root)
        preview_window.title("Vista previa del XML")
        preview_window.geometry("800x600")

        text_area = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, tei_content)
        text_area.configure(state='disabled')

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error en vista_previa_xml:\n{error_details}")
        messagebox.showerror("Error", f"Se ha producido un error:\n{e}\n\nDetalles técnicos guardados en consola.")

def vista_previa_html(entry_main, entry_com, entry_apa, entry_meta, header_mode="prolope"):
    """
    Genera un archivo HTML temporal para previsualizar el TEI renderizado con CETEIcean.
    """
    main_file = entry_main.get()
    com_file  = entry_com.get()
    apa_file  = entry_apa.get()

    if not main_file:
        messagebox.showerror("Error", "Seleccione al menos el DOCX Principal!")
        return

    try:
        tei_content = convert_docx_to_tei(
            main_docx=main_file,
            notas_docx=com_file if com_file else None,
            aparato_docx=apa_file  if apa_file else None,
            metadata_docx=entry_meta.get() or None,
            output_file=None,
            save=False,
            header_mode=header_mode
        )

        html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Edición Digital</title>
    <style>
    {ESTILOS_CSS}
    </style>
</head>
<body>
    <!-- Botón de toggle del menú -->
    <button id="nav-toggle" class="nav-toggle-btn" title="Mostrar/Ocultar menú">☰</button>
    
    <!-- Menú de navegación lateral -->
    <nav id="nav-menu">
        <div class="nav-header">
            <span class="nav-title">Navegación</span>
        </div>
        <ul id="nav-list">
            <!-- Se llenará dinámicamente con JavaScript -->
        </ul>
    </nav>
    
    <div id="tei"></div>

    <script>
    {CETEI_JS}
    </script>

    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const ceteiInstance = new CETEI();
        const htmlNode = ceteiInstance.makeHTML5(`{tei_content}`);
        document.getElementById("tei").appendChild(htmlNode);
        
        // Generar menú de navegación después de renderizar el TEI
        setTimeout(buildNavigationMenu, 100);
    }});
    
    function buildNavigationMenu() {{
        const navList = document.getElementById('nav-list');
        const menuItems = [];
        
        // 1. Metadatos (teiHeader)
        const teiHeader = document.querySelector('tei-teiheader, teiHeader');
        if (teiHeader) {{
            teiHeader.setAttribute('id', 'metadatos');
            menuItems.push({{
                id: 'metadatos',
                text: 'Metadatos',
                level: 1,
                element: teiHeader
            }});
        }}
        
        // 2. Prólogo (front)
        const prologo = document.querySelector('tei-div[type="Introducción"], [xml\\\\:id="prologo"]');
        if (prologo) {{
            menuItems.push({{
                id: 'prologo',
                text: 'Prólogo',
                level: 1,
                element: prologo
            }});
            
            // Subsecciones del prólogo
            const subsecciones = prologo.querySelectorAll('tei-div[type="subsection"]');
            subsecciones.forEach((sub, idx) => {{
                const head = sub.querySelector('tei-head');
                if (head) {{
                    const subId = 'prologo-sub-' + (idx + 1);
                    sub.setAttribute('id', subId);
                    // Clonar el head para eliminar notas y obtener texto limpio
                    const cleanHead = head.cloneNode(true);
                    cleanHead.querySelectorAll('tei-note, note').forEach(note => note.remove());
                    const headText = cleanHead.textContent.trim();
                    
                    // Si el título empieza con "ACTO", es nivel 3 (argumento por actos)
                    // Si no, es nivel 2 (subsección normal del prólogo)
                    if (headText.match(/^Acto/i)) {{
                        menuItems.push({{
                            id: subId,
                            text: headText,
                            level: 3,
                            element: sub
                        }});
                    }} else {{
                        menuItems.push({{
                            id: subId,
                            text: headText,
                            level: 2,
                            element: sub
                        }});
                    }}
                }}
            }});
        }}
        
        // 3. Título de la comedia
        const titulo = document.querySelector('tei-head[type="mainTitle"]');
        if (titulo) {{
            titulo.setAttribute('id', 'titulo');
            // Clonar para eliminar notas y obtener texto limpio
            const cleanTitulo = titulo.cloneNode(true);
            cleanTitulo.querySelectorAll('tei-note, note').forEach(note => note.remove());
            menuItems.push({{
                id: 'titulo',
                text: cleanTitulo.textContent.trim(),
                level: 1,
                element: titulo
            }});
        }}
        
        // 4. Dedicatoria
        const dedicatoria = document.querySelector('tei-div[type="dedicatoria"]');
        if (dedicatoria) {{
            dedicatoria.setAttribute('id', 'dedicatoria');
            const head = dedicatoria.querySelector('tei-head');
            let headText = 'Dedicatoria';
            if (head) {{
                const cleanHead = head.cloneNode(true);
                cleanHead.querySelectorAll('tei-note, note').forEach(note => note.remove());
                headText = cleanHead.textContent.trim();
            }}
            menuItems.push({{
                id: 'dedicatoria',
                text: headText,
                level: 2,
                element: dedicatoria
            }});
        }}
        
        // 5. Lista de personajes
        const personajes = document.querySelector('tei-div[type="castList"]');
        if (personajes) {{
            personajes.setAttribute('id', 'personajes');
            const head = personajes.querySelector('tei-head[type="castListTitle"], tei-head');
            let headText = 'Personajes';
            if (head) {{
                const cleanHead = head.cloneNode(true);
                cleanHead.querySelectorAll('tei-note, note').forEach(note => note.remove());
                headText = cleanHead.textContent.trim();
            }}
            menuItems.push({{
                id: 'personajes',
                text: headText,
                level: 2,
                element: personajes
            }});
        }}
        
        // 6. Actos (nivel 2, igual que Dedicatoria y Personajes)
        const actos = document.querySelectorAll('tei-div[subtype="ACTO"]');
        actos.forEach((acto, idx) => {{
            const actoId = 'acto' + (idx + 1);
            acto.setAttribute('id', actoId);
            const head = acto.querySelector('tei-head[type="acto"]');
            let headText = 'Acto ' + (idx + 1);
            if (head) {{
                const cleanHead = head.cloneNode(true);
                cleanHead.querySelectorAll('tei-note, note').forEach(note => note.remove());
                headText = cleanHead.textContent.trim();
            }}
            menuItems.push({{
                id: actoId,
                text: headText,
                level: 2,
                element: acto
            }});
        }});
        
        // Construir el HTML del menú
        menuItems.forEach(item => {{
            const li = document.createElement('li');
            li.className = 'nav-item nav-level-' + item.level;
            
            const a = document.createElement('a');
            a.href = '#' + item.id;
            a.textContent = item.text;
            a.addEventListener('click', function(e) {{
                e.preventDefault();
                item.element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                
                // Resaltar brevemente la sección
                item.element.classList.add('nav-highlight');
                setTimeout(() => item.element.classList.remove('nav-highlight'), 1500);
            }});
            
            li.appendChild(a);
            navList.appendChild(li);
        }});
        
        // Toggle del menú
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        navToggle.addEventListener('click', function() {{
            navMenu.classList.toggle('nav-open');
            document.body.classList.toggle('nav-open');
        }});
    }}
    </script>
</body>
</html>
"""


        tmp_file = tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8")
        tmp_file.write(html_template)
        tmp_file.close()
        webbrowser.open(f"file://{tmp_file.name}")

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error en vista_previa_html:\n{error_details}")
        messagebox.showerror("Error", f"Se ha producido un error:\n{e}\n\nDetalles técnicos guardados en consola.")
