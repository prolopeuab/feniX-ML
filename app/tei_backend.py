# ==========================================
# feniX-ML: Marcado automático de DOCX a TEI/XML
# Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.
# Grupo de investigación PROLOPE, Universitat Autònoma de Barcelona
# Descripción: Funciones para convertir textos teatrales en formato DOCX a TEI/XML, incluyendo manejo de notas, metadatos y validaciones.
# Este script debe utilizarse junto a visualizacion.py, gui.py y main.py.
# ==========================================

# ==== IMPORTACIONES ====
import os
import re
import unicodedata
import zipfile
from lxml import etree
from docx import Document
from docx.oxml.ns import qn
from difflib import get_close_matches
from typing import Optional


# ==== EXTRACCIÓN Y PROCESAMIENTO DE NOTAS EN EL PRÓLOGO ====
# Funciones para extraer y procesar notas a pie de página del prólogo o introducción.

def extract_intro_footnotes(docx_path):
    """
    Extrae todas las notas a pie de página de un archivo DOCX.
    Devuelve un diccionario {id: note_text}.
    """
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    footnote_dict = {}

    with zipfile.ZipFile(docx_path) as docx_zip:
        with docx_zip.open("word/footnotes.xml") as footnote_file:
            root = etree.parse(footnote_file).getroot()

            for note in root.xpath("//w:footnote[not(@w:type='separator')]", namespaces=ns):
                note_id = note.get(qn("w:id"))
                texts = note.xpath(".//w:t", namespaces=ns)
                full_text = "".join(t.text for t in texts if t is not None).strip()
                if full_text:
                    footnote_dict[note_id] = full_text

    return footnote_dict

def extract_text_with_intro_notes(para, footnotes_intro):
    """
    Extrae el texto de un párrafo, insertando las notas en el lugar correspondiente.
    """
    text = ""
    for run in para.runs:
        run_element = run._element
        refs = run_element.findall(".//w:footnoteReference", namespaces=run_element.nsmap)
        if refs:
            for ref in refs:
                note_id = ref.get(qn("w:id"))
                note_text = footnotes_intro.get(note_id, "")
                text += f'<note type="intro" n="{note_id}">{note_text}</note>'
        else:
            if run.italic:
                text += f'<hi rend="italic">{run.text}</hi>'
            else:
                text += run.text
    return text.strip()

# ==== MANEJO DE BLOQUES ESTRUCTURALES TEI ====
def close_current_blocks(tei, state):
    """
    Cierra los bloques abiertos en el estado actual del documento TEI.
    """
    # Cierra los bloques abiertos en el estado actual
    if state.get("in_sp"):
        tei.append('        </sp>')
        state["in_sp"] = False
    if state.get("in_cast_list"):
        tei.append('          </castList>')
        tei.append('        </div>')
        state["in_cast_list"] = False
    if state.get("in_dedicatoria"):
        tei.append('        </div>')
        state["in_dedicatoria"] = False
    if state.get("in_act"):
        tei.append('        </div>')
        state["in_act"] = False

# ==== FUNCIONES DE SOPORTE PARA TEXTO ====
def extract_text_with_italics(para):
    """
    Extrae el texto de un párrafo, preservando las cursivas.
    """
    # Recorre los runs del párrafo y envuelve en <hi rend="italic"> si es cursiva
    text = ""
    for run in para.runs:
        if run.italic:
            text += f'<hi rend="italic">{run.text}</hi>'
        else:
            text += run.text
    return text.strip()

def merge_italic_text(text):
    """
    Fusiona secuencias consecutivas de etiquetas <hi rend="italic">...</hi> en una sola.
    """
    # Busca una o más ocurrencias consecutivas de <hi rend="italic">...</hi>
    pattern = re.compile(r'((?:<hi rend="italic">.*?</hi>\s*)+)', re.DOTALL)
    def replacer(match):
        segment = match.group(1)
        # Extrae todo el contenido interno de los tags
        inner_texts = re.findall(r'<hi rend="italic">(.*?)</hi>', segment, re.DOTALL)
        # Une todo en una sola cadena (sin espacios adicionales)
        merged = ''.join(inner_texts).strip()
        return f'<hi rend="italic">{merged}</hi>'
    return pattern.sub(replacer, text)

def generate_filename(title):
    """
    Genera un nombre de archivo a partir de las primeras tres palabras del título.
    """
    # Toma las primeras tres palabras del título y elimina espacios, comas y puntos
    words = title.split()[:3]
    filename = '_'.join(words).replace(' ', '_').replace(',', '').replace('.', '')
    return filename

def find_who_id(speaker, characters):
    """
    Busca el xml:id correcto de un personaje en la lista de personajes, usando coincidencia flexible.
    """
    # Limpia el nombre del personaje para facilitar la comparación
    speaker_cleaned = re.sub(r'[\s\[\]]+', '_', speaker).strip()

    # Coincidencia exacta
    if speaker.strip() in characters:
        return characters[speaker.strip()]

    # Coincidencia parcial
    for name, role_id in characters.items():
        if speaker.strip() in name or speaker_cleaned in role_id:
            return role_id

    # Coincidencia difusa (fuzzy matching) como último recurso
    close_matches = get_close_matches(speaker.strip(), characters.keys(), n=1, cutoff=0.8)
    if close_matches:
        return characters[close_matches[0]]

    return ""


# ==== PROCESAMIENTO DE METADATOS Y FRONT-MATTER ====
def parse_metadata_docx(path):
    """
    Extrae metadatos de un archivo .docx estructurado en tablas y construye un teiHeader TEI/XML completo.
    """
    doc = Document(path)
    tables = doc.tables

    if len(tables) < 3:
        raise ValueError("❌ El documento de metadatos debe contener al menos 3 tablas.")

    # Tabla 1: Metadatos principales
    main_meta = {}
    for row in tables[0].rows:
        if len(row.cells) >= 2:
            key = row.cells[0].text.strip()
            value = row.cells[1].text.strip()
            main_meta[key] = value

    # Tabla 2: sourceDesc
    source_meta = {}
    for row in tables[1].rows:
        if len(row.cells) >= 2:
            key = row.cells[0].text.strip()
            value = row.cells[1].text.strip()
            source_meta[key] = value

    # Tabla 3: listWit (salta la primera fila)
    witnesses = []
    for i, row in enumerate(tables[2].rows):
        if i == 0:
            continue  # salta la fila guía "SIGLA TESTIMONIO | DESCRIPCIÓN"
        if len(row.cells) >= 2:
            siglum = row.cells[0].text.strip()

            # Extrae el contenido de la segunda celda manteniendo la cursiva
            desc_parts = []
            for run in row.cells[1].paragraphs[0].runs:
                if run.italic:
                    desc_parts.append(f'<hi rend="italic">{run.text}</hi>')
                else:
                    desc_parts.append(run.text)
            desc = ''.join(desc_parts).strip()

            if siglum and desc:
                witnesses.append((siglum, desc))

    # Construcción del teiHeader
    tei = ['<teiHeader>', '  <fileDesc>', '    <titleStmt>']

    tei.append(f'      <title>{main_meta.get("Título comedia", "")}</title>')
    tei.append(f'      <author><name>{main_meta.get("Autor", "")}</name></author>')

    if 'Editor' in main_meta:
        tei.append(f'      <editor>{main_meta["Editor"]}</editor>')

    if 'Responsable/s revisión' in main_meta:
        tei.append('      <respStmt>')
        tei.append('        <resp>Edición crítica digital revisada filológicamente por</resp>')
        for name in main_meta['Responsable/s revisión'].split(','):
            tei.append(f'        <persName>{name.strip()}</persName>')
        tei.append('      </respStmt>')

    if 'Responsable marcado automático' in main_meta:
        tei.append('      <respStmt>')
        tei.append('        <resp>Marcado XML-TEI automático revisado por</resp>')
        for name in main_meta['Responsable marcado automático'].split(','):
            tei.append(f'        <persName>{name.strip()}</persName>')
        tei.append('      </respStmt>')

    tei.append('      <respStmt>')
    tei.append('        <resp>Codificado según los criterios de</resp>')
    tei.append('        <name ref="https://datos.bne.es/entidad/XX4849774.html">Grupo de investigación PROLOPE, de la Universitat Autònoma de Barcelona</name>')
    tei.append('      </respStmt>')

    tei.extend(['    </titleStmt>', '    <editionStmt>'])
    tei.append(f'      <edition>Versión {main_meta.get("Versión", "")}</edition>')
    tei.extend(['    </editionStmt>', '    <publicationStmt>'])
    tei.append(f'      <publisher>{main_meta.get("Publicado por", "")}</publisher>')
    tei.append(f'      <pubPlace>{main_meta.get("Lugar publicación", "")}</pubPlace>')
    tei.append(f'      <date>{main_meta.get("Fecha publicación", "")}</date>')
    tei.extend(['    </publicationStmt>', '    <seriesStmt>'])
    tei.append('      <title>Biblioteca Digital PROLOPE</title>')
    tei.append('      <respStmt>')
    tei.append('        <resp>Dirección de</resp>')
    tei.append('        <persName ref="https://orcid.org/0000-0002-7429-9709"><forename>Ramón</forename> <surname>Valdés Gázquez</surname></persName>')
    tei.append('      </respStmt>')
    tei.append('      <idno type="URI">https://bibdigitalprolope.com/</idno>')
    tei.append('    </seriesStmt>')

    # sourceDesc
    tei.extend(['    <sourceDesc>', '      <biblStruct xml:lang="es">', '        <monogr>'])
    tei.append('          <author>')
    tei.append('            <persName ref="http://datos.bne.es/persona/XX1719671"><forename>Félix Lope</forename><surname>de Vega Carpio</surname></persName>')
    tei.append('          </author>')
    tei.append(f'          <title type="main">{source_meta.get("Titulo comedia", "")}</title>')
    if "Subtítulo" in source_meta:
        tei.append(f'          <title type="alt">{source_meta.get("Subtítulo", "")}</title>')
    if 'Editor' in main_meta:
        tei.append(f'        <editor>{main_meta["Editor"]}</editor>')
    tei.append(f'          <title type="main">{source_meta.get("Titulo comedia", "")}</title>')
    tei.append(f'          <title type="s">{source_meta.get("Título volumen", "")}</title>')
    tei.append(f'          <title type="a">Parte {source_meta.get("Parte", "")}</title>')
    if 'Coordinadores volumen' in source_meta:
        tei.append('        <respStmt>')
        tei.append('          <resp>Coordinación del volumen a cargo de</resp>')
        for name in source_meta['Coordinadores volumen'].split(','):
            tei.append(f'          <persName>{name.strip()}</persName>')
        tei.append('        </respStmt>')
    tei.append(f'          <title type="s">{source_meta.get("Título volumen", "")}</title>')
    tei.append(f'          <title type="a">Parte {source_meta.get("Parte", "")}</title>')
    tei.append('          <availability status="restricted">')
    tei.append('           <p>Todos los derechos reservados.</p>')
    tei.append('          </availability>')
    tei.append('          <imprint>')
    tei.append(f'            <pubPlace>{source_meta.get("Lugar publicación", "")}</pubPlace>')
    tei.append(f'            <publisher>{source_meta.get("Publicado por", "")}</publisher>')
    tei.append(f'            <date>{source_meta.get("Fecha publicación", "")}</date>')
    tei.append(f'            <biblScope unit="volume" n="{source_meta.get("Volumen", "")}">vol. {source_meta.get("Volumen", "")}</biblScope>')
    tei.append(f'            <biblScope unit="page">{source_meta.get("Páginas", "")}</biblScope>')
    tei.append('          </imprint>')
    tei.append('        </monogr>')
    tei.append('      </biblStruct>')
    tei.append('  <encodingDesc>')
    tei.append('    <editorialDecl>')
    tei.append('      <p>Este marcado ha sido realizado utilizando la aplicación FéniX-ML, desarrollada por Anna Abate, Emanuele Leboffe y David Merino Recalde.</p>')
    tei.append('    </editorialDecl>')
    tei.append('  </encodingDesc>')

    # listWit
    tei.append('      <listWit>')
    for siglum, desc in witnesses:
        tei.append(f'        <witness xml:id="{siglum}">')
        tei.append(f'          <label>{desc}</label>')
        tei.append('        </witness>')
    tei.append('      </listWit>')

    tei.extend(['    </sourceDesc>', '  </fileDesc>', '</teiHeader>'])

    return "\n".join(tei)

def process_front_paragraphs_with_tables(doc, front_paragraphs, footnotes_intro):
    """
    Procesa los párrafos del front-matter, incluyendo tablas, generando el bloque <front> del TEI.
    """
    tei_front = []
    subsection_open = False
    subsection_n = 1
    current_section = None
    paragraph_buffer = []
    head_inserted = False
    processed_tables = set()  # Para evitar procesar tablas múltiples veces

    def flush_paragraph_buffer():
        nonlocal paragraph_buffer
        for p in paragraph_buffer:
            text = extract_text_with_intro_notes(p, footnotes_intro)
            if p.style and p.style.name == "Cita":
                tei_front.append(f'          <cit rend="blockquote">')
                tei_front.append(f'            <quote>{text}</quote>')
                tei_front.append(f'          </cit>')
            elif text.strip():
                tei_front.append(f'          <p>{text.strip()}</p>')
        paragraph_buffer.clear()

    def process_nearby_tables():
        """Procesa tablas que aparecen en el contexto actual."""
        for i, table in enumerate(doc.tables):
            if i in processed_tables:
                continue
            
            # Procesar todas las tablas no procesadas en la sección actual
            # (en el futuro se podría refinar esto para detectar posición exacta)
            if current_section and "sinopsis" in current_section:
                tei_front.append(process_table_to_tei(table, footnotes_intro))
                processed_tables.add(i)

    for i, para in enumerate(front_paragraphs):
        raw = extract_text_with_intro_notes(para, footnotes_intro)
        text = para.text.strip() if para.text else ""
        if not text:
            continue

        # 🔹 Ignora "Introducción"
        if text.lower() == "introducción":
            continue

        # 🔹 Gestión del título principal "PRÓLOGO"
        if not head_inserted and "prólogo" in text.lower():
            flush_paragraph_buffer()
            tei_front.append(f'        <head type="divTitle" subtype="MenuLevel_1">PRÓLOGO</head>')
            head_inserted = True
            continue

        # 🔹 Reconocimiento de subtítulo con almohadilla
        if text.startswith("#"):
            flush_paragraph_buffer()
            title = text.lstrip("#").strip()
            if title.lower() == "prólogo":
                continue  # ignora duplicado
            if subsection_open:
                tei_front.append('        </div>')
            tei_front.append(f'        <div type="subsection" n="{subsection_n}">')
            tei_front.append(f'          <head type="divTitle" subtype="MenuLevel_2">{title}</head>')
            subsection_open = True
            current_section = title.lower()
            subsection_n += 1

            # 🔹 Procesar tablas después de abrir la subsección
            process_nearby_tables()
            continue

        # 🔹 Añade al buffer
        paragraph_buffer.append(para)

    flush_paragraph_buffer()

    if subsection_open:
        tei_front.append('        </div>')  # cierra la última subsection

    return "\n".join(tei_front)

def process_table_to_tei(table, footnotes_intro=None):
    """
    Convierte una tabla DOCX en una tabla TEI, incluyendo notas al pie.
    """
    if footnotes_intro is None:
        footnotes_intro = {}
        
    ncols = len(table.columns)
    tei = ['<table rend="rules">']

    # 1) Filas título
    hdr = table.rows[0]
    tei.append('  <row>')
    for cell in hdr.cells:
        raw = extract_text_with_intro_notes(cell.paragraphs[0], footnotes_intro)
        tei.append(
            '    <cell rend="both">\n'
            f'      <hi rend="italic" style="padding-left:3em; font-size:13pt; font-weight:bold">{raw}</hi>\n'
            '    </cell>'
        )
    tei.append('  </row>')

    # 2) Filas vacías
    tei.append('  <row>')
    for _ in range(ncols):
        tei.append('    <cell rend="both"> </cell>')
    tei.append('  </row>')

    # 3) Filas datos
    for row in table.rows[1:]:
        texts = [c.text.strip() for c in row.cells]
        non_empty = [t for t in texts if t]

        
        if len(non_empty) == 1 and texts[0] and all(not t for t in texts[1:]):
            raw = extract_text_with_intro_notes(row.cells[0].paragraphs[0], footnotes_intro)
            tei.extend([
                '  <row>',
                f'    <cell rend="both" cols="{ncols}">',
                f'      <hi rend="italic" style="font-size:13pt; font-weight:bold;">{raw}</hi>',
                '    </cell>',
                '  </row>',
            ])
            continue

        # Filas resumen
        key = texts[0].lower()
        is_summary = key in ("total", "resumen") and all(texts)
        
        tei.append('  <row>')
        for idx, cell in enumerate(row.cells):
            txt = cell.text.strip()
            if not txt:
                tei.append('    <cell rend="both"> </cell>')
                continue
            raw = extract_text_with_intro_notes(cell.paragraphs[0], footnotes_intro)
            if is_summary:
                style = "padding-left:3em; font-size:11pt; font-weight:bold"
                if key == "total":
                    rend = ' rend="italic"' if idx == 0 else ""
                else:
                    rend = ' rend="italic"'
            else:
                style = "padding-left:3em; font-size:11pt"
                rend = ""
            tei.append(
                f'    <cell rend="both">\n'
                f'      <hi{rend} style="{style}">{raw}</hi>\n'
                '    </cell>'
            )
        tei.append('  </row>')

    tei.append('</table>')
    return "\n".join(tei)

# ==== EXTRACCIÓN DE NOTAS DE notas Y APARATO ====

def extract_notes_with_italics(docx_path: str) -> dict:
    """
    Extrae notas o aparato de un DOCX.
    Devuelve un dict donde las claves pueden ser int (versos) o str (palabras)
    y los valores el texto de la nota.
    """
    notes: dict = {}
    if not docx_path or not os.path.exists(docx_path):
        return notes

    doc = Document(docx_path)
    for para in doc.paragraphs:
        text = extract_text_with_italics(para).strip()

        # Notas tipo verso: "1: contenido"
        match_verse = re.match(r'^(\d+):\s*(.*)', text)
        # Notas tipo @palabra@: "@palabra@: contenido"
        match_single = re.match(r'^@([^@]+?):\s*(.*)', text)

        if match_verse:
            verse_num = int(match_verse.group(1))
            notes[verse_num] = match_verse.group(2).strip()
        elif match_single:
            key = match_single.group(1).strip()
            if key not in notes:
                notes[key] = match_single.group(2).strip()

    return notes


# ==== PROCESAMIENTO DE NOTAS Y APARATO ====

def process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, section):
    """
    Sustituye marcadores @palabra en el texto por notas TEI con xml:ids únicos.
    - nota_notes y aparato_notes son dicts con claves normalizadas.
    - annotation_counter es un dict que lleva el conteo de repeticiones por sección.
    - section es el nombre de la sección (p.ej. 'p', 'speaker', etc.).
    """
    if not text:
        return ""

    # Aseguramos dicts válidos
    nota_notes = nota_notes or {}
    aparato_notes    = aparato_notes    or {}

    # Función de normalización para claves
    def normalize_word(word):
        if isinstance(word, int):
            return word
        # Quitamos tags <hi> y descomponemos acentos
        plain = re.sub(r'<hi rend="italic">(.*?)</hi>', r'\1', word)
        normalized = unicodedata.normalize('NFKD', plain)
        normalized = normalized.encode('ASCII', 'ignore').decode('utf-8').lower().strip()
        return normalized

    # Normalizamos claves de las notas
    nota_notes_norm = {
        normalize_word(k): v
        for k, v in nota_notes.items()
        if isinstance(k, str)
    }
    aparato_notes_norm = {
        normalize_word(k): v
        for k, v in aparato_notes.items()
        if isinstance(k, str)
    }

    # Unificamos todas las notas en un solo dict
    all_notes = {**nota_notes_norm, **aparato_notes_norm}

    new_text = text.strip()
    # Buscamos todos los marcadores '@palabra'
    matches = re.findall(r'@(\w+)', text)

    for phrase in matches:
        if not phrase:
            continue
        phrase_to_replace = f"@{phrase}"
        key = normalize_word(phrase)

        if key in all_notes:
            # Gestionamos el contador por sección
            section_counters = annotation_counter.setdefault(section, {})
            count = section_counters.get(key, 0) + 1
            section_counters[key] = count

            # Creamos xml:id válido
            xml_id = f"{key}_{section}_{count}"
            xml_id = re.sub(r'\s+', '_', xml_id)
            xml_id = re.sub(r'[^a-zA-Z0-9_]', '', xml_id)
            xml_id = xml_id.lower()

            # Construimos los posibles <note>
            note_str = ""
            if key in nota_notes_norm:
                note_str += f'<note subtype="nota" xml:id="{xml_id}">{nota_notes_norm[key]}</note>'
            if key in aparato_notes_norm:
                note_str += f'<note subtype="aparato"     xml:id="{xml_id}">{aparato_notes_norm[key]}</note>'

            # Sustituimos solo la primera ocurrencia
            new_text = new_text.replace(phrase_to_replace, f"{phrase}{note_str}", 1)

    # Reagrupamos cursivas consecutivas
    new_text = merge_italic_text(new_text)
    return new_text


# ==== FUNCIÓN PRINCIPAL DE CONVERSIÓN DOCX → TEI ====
def convert_docx_to_tei(
    main_docx: str,
    notas_docx: Optional[str] = None,
    aparato_docx: Optional[str] = None,
    metadata_docx: Optional[str] = None,  
    tei_header: Optional[str] = None,
    output_file: Optional[str] = None,
    save: bool = True
) -> Optional[str]:
    """
    Convierte uno o más DOCX a un XML-TEI completo.
    """
    #Chequeo de existencia del principal
    if not main_docx.lower().endswith(".docx"):
        raise ValueError(f"Se esperaba un .docx, pero se obtuvo: {main_docx}")
    if not os.path.exists(main_docx):
        raise FileNotFoundError(f"No existe el archivo principal: {main_docx}")

    # Generación del header TEI a partir de metadata_docx si se proporciona
    if metadata_docx:
        if not os.path.exists(metadata_docx):
            raise FileNotFoundError(f"No existe el archivo de metadatos: {metadata_docx}")
        try:
            tei_header = parse_metadata_docx(metadata_docx)
        except Exception as e:
            raise RuntimeError(f"No se pudo parsear metadata DOCX '{metadata_docx}': {e}")
    elif not tei_header:
        # Cabecera mínima de reserva
        tei_header_respaldo = "<teiHeader>…</teiHeader>"

    header = tei_header if tei_header else tei_header_respaldo

    # Carga del DOCX principal
    doc = Document(main_docx)

    # --- SEPARACIÓN FRONT/BODY BASADA EN 'Titulo_comedia' ---

    # 1) Busca la posición del primer párrafo con style 'Titulo_comedia'
    title_idx = next(
        (i for i, p in enumerate(doc.paragraphs)
        if p.style and p.style.name == "Titulo_comedia"),
        None
    )
    if title_idx is None:
        raise RuntimeError("No se encontró ningún párrafo con estilo 'Titulo_comedia' en el documento")

    # 2) Divide la lista de párrafos en front y body
    front_paragraphs = list(doc.paragraphs[:title_idx])
    body_paragraphs  = list(doc.paragraphs[title_idx:])



    # --- Extracción del título usando title_idx de la separación front/body ---
    if title_idx is None:
        # Ya habíamos detectado esto antes; si quisieras recuperar aquí:
        raise RuntimeError("No se encontró ningún párrafo con estilo 'Titulo_comedia' para extraer el título.")

    raw_title = doc.paragraphs[title_idx].text.strip()
    # Quitar cualquier '@' u otro carácter problemático
    clean_title = re.sub(r'@', '', raw_title)
    # Generar la clave/slug a partir del título limpio
    title_key   = generate_filename(clean_title)


    # --- Determinación y validación de rutas de notas y aparato ---
    nota_notes = {}
    if notas_docx:
        if not notas_docx.lower().endswith(".docx"):
            raise ValueError(f"El archivo de notas debe ser .docx: {notas_docx}")
        if not os.path.exists(notas_docx):
            raise FileNotFoundError(f"No existe el archivo de notas: {notas_docx}")
        nota_notes = extract_notes_with_italics(notas_docx)

    aparato_notes = {}
    if aparato_docx:
        if not aparato_docx.lower().endswith(".docx"):
            raise ValueError(f"El archivo de aparato debe ser .docx: {aparato_docx}")
        if not os.path.exists(aparato_docx):
            raise FileNotFoundError(f"No existe el archivo de aparato: {aparato_docx}")
        aparato_notes = extract_notes_with_italics(aparato_docx)

    
    # Contadores y estado
    annotation_counter = {}
    state = {
        "in_sp": False,
        "in_cast_list": False,
        "in_dedicatoria": False,
        "in_act": False
    }
    characters = {}
    act_counter = 0
    verse_counter = 1
    current_milestone = None   # ← inicializado aquí

    # Título procesado con el mismo contador de anotaciones
    processed_title = process_annotations_with_ids(
        clean_title,
        nota_notes,
        aparato_notes,
        annotation_counter,
        "head"
    )

    # Notas introductorias
    footnotes_intro = extract_intro_footnotes(main_docx)

    # Para el bucle de Personaje
    ultimo_speaker_id = None


    # --- Construcción de <front> y apertura de <body> ---
    tei = [
        '<?xml version="1.0" encoding="UTF-8"?>',  # línea XML
        '<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" '
        'schematypens="http://relaxng.org/ns/structure/1.0"?>',
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
        header,                       # ya generado arriba
        '  <text>',
        '    <front>',
        '      <div type="Introducción">'
    ]

    # Inserta el contenido de <front>, incluyendo notas introductorias y tablas
    tei.append(process_front_paragraphs_with_tables(doc, front_paragraphs, footnotes_intro))

    # Cerramos el front y abrimos el body con el título principal
    tei.extend([
        '      </div>',    # cierra <div type="Introducción">
        '    </front>',
        '    <body>',
        '      <div type="Texto" subtype="TEXTO">',
        f'        <head type="mainTitle">{processed_title}</head>',
    ])


    # Recorre todos los párrafos del cuerpo para identificar y procesar cada bloque estilístico
    for para in body_paragraphs:
        text = extract_text_with_italics(para).strip()
        style = para.style.name if para.style else "Normal"

        # 1) Detección de estrofas marcadas con $nombreMilestone
        milestone_match = re.match(r'^\$(\w+)', text)
        if milestone_match:
            current_milestone = milestone_match.group(1)
            continue  # saltamos el resto: sólo guardamos el tipo de estrofa

        # 2) Antes de abrir un nuevo bloque estilístico, cerramos los que estén abiertos
        if style in ["Epigr_Dramatis", "Acto", "Epigr_Dedic"]:
            close_current_blocks(tei, state)


        if style == "Epigr_Dedic":
            tei.append('        <div type="dedicatoria">')
            tei.append(f'          <head>{text}</head>')
            state["in_dedicatoria"] = True

        elif style == "Epigr_Dramatis":
            tei.append('        <div type="castList">')
            tei.append(f'            <head>{text}</head>')
            tei.append('          <castList>')
            state["in_cast_list"] = True


        elif style == "Dramatis_lista":
            role_name = text
            if role_name:
                role_id = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_-]+', '_', role_name)
                tei.append(f'            <castItem><role xml:id="{role_id}">{role_name}</role></castItem>')
                characters[role_name] = role_id

        elif style == "Acto":
            act_counter += 1
            tei.append(f'        <div type="subsection" subtype="ACTO" n="{act_counter}">')
            tei.append(f'          <head type="acto">{text}</head>')
            state["in_act"] = True

        elif style == "Prosa":
            processed_text = process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, "p")
            if processed_text.strip():
                tei.append(f'          <p>{processed_text}</p>')

        elif style == "Verso":
            if state["in_dedicatoria"]:
                tei.append(f'          <l>{text}</l>')
            elif state["in_sp"]:
                if current_milestone:
                    tei.append(f'            <milestone unit="stanza" type="{current_milestone}"/>')
                    current_milestone = None
                verse_text = text
                if verse_counter in nota_notes:
                    verse_text += f'<note subtype="nota" n="{verse_counter}">{nota_notes[verse_counter]}</note>'
                if verse_counter in aparato_notes:
                    verse_text += f'<note subtype="aparato" n="{verse_counter}">{aparato_notes[verse_counter]}</note>'
                tei.append(f'            <l n="{verse_counter}">{verse_text}</l>')
                verse_counter += 1

        elif style == "Laguna":
            # Laguna de extensión incierta - no incrementa el contador de versos
            processed_text = process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, "gap")
            if state["in_sp"]:
                if current_milestone:
                    tei.append(f'            <milestone unit="stanza" type="{current_milestone}"/>')
                    current_milestone = None
                tei.append(f'            <gap>{processed_text}</gap>')
            elif state["in_dedicatoria"]:
                tei.append(f'          <gap>{processed_text}</gap>')

        elif style == "Partido_incial":
            # Almacenar información del verso partido para procesamiento posterior
            if not hasattr(state, "pending_split_verse"):
                state["pending_split_verse"] = {}
            
            state["pending_split_verse"] = {
                "verse_number": verse_counter,
                "initial_text": text,
                "parts": [text],
                "has_notes": verse_counter in nota_notes or verse_counter in aparato_notes
            }
            
            verse_text = text
            if verse_counter in nota_notes:
                verse_text += f'<note subtype="nota" n="{verse_counter}">{nota_notes[verse_counter]}</note>'
            if verse_counter in aparato_notes:
                verse_text += f'<note subtype="aparato" n="{verse_counter}">{aparato_notes[verse_counter]}</note>'
            tei.append(f'            <l part="I" n="{verse_counter}">{verse_text}</l>')
            verse_counter += 1

        elif style == "Partido_medio":
            # Añadir parte media al verso partido pendiente
            if hasattr(state, "pending_split_verse") and state.get("pending_split_verse"):
                state["pending_split_verse"]["parts"].append(text)
            tei.append(f'            <l part="M">{text}</l>')

        elif style == "Partido_final":
            # Completar el verso partido y limpiar estado
            if hasattr(state, "pending_split_verse") and state.get("pending_split_verse"):
                state["pending_split_verse"]["parts"].append(text)
                # El verso partido está completo, limpiar estado
                state["pending_split_verse"] = None
            tei.append(f'            <l part="F">{text}</l>')

        elif style == "Acot":
            processed_text = process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, "stage")
            if state["in_sp"]:
                tei.append('        </sp>')
                state["in_sp"] = False
            tei.append(f'        <stage>{processed_text}</stage>')

        elif style == "Personaje":
            who_id = find_who_id(text, characters)
            processed = process_annotations_with_ids(
                text, nota_notes, aparato_notes, annotation_counter, "speaker"
            )

            # 🔒 Cierra <sp> anterior si es necesario
            if state["in_sp"]:
                tei.append('        </sp>')
                state["in_sp"] = False

            # 🎯 Si es el mismo personaje anterior, no insertar who ni speaker
            if who_id == ultimo_speaker_id:
                tei.append('        <sp>')
            else:
                tei.append(f'        <sp who="#{who_id}">')
                tei.append(f'          <speaker>{processed}</speaker>')
                ultimo_speaker_id = who_id

            state["in_sp"] = True

        elif style == "Epigr_final":
            processed_text = process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, "trailer")
            if processed_text.strip():
                tei.append(f'          <trailer>{processed_text}</trailer>')



    # Cierre final de todos los bloques aún abiertos
    close_current_blocks(tei, state)

    # Verificar si hay versos partidos incompletos al final del procesamiento
    if hasattr(state, "pending_split_verse") and state.get("pending_split_verse"):
        pending = state["pending_split_verse"]
        print(f"⚠️ Advertencia: Verso partido incompleto detectado durante procesamiento:")
        print(f"   Verso {pending['verse_number']}: '{pending['initial_text'][:50]}...'")
        print(f"   - Falta Partido_final para completar el verso")

    # Cierre de secciones TEI
    tei.append('      </div>')  # cierra Texto
    tei.append('    </body>')
    tei.append('  </text>')
    tei.append('</TEI>')



    # Serializamos el TEI a string
    tei = [fragment for fragment in tei if isinstance(fragment, str)]
    tei_str = "\n".join(tei)

    # Si no queremos guardar en disco, devolvemos el string
    if not save:
        return tei_str

    # Si llegamos aquí, save == True: escribimos el fichero
    if not output_file:
        # Generamos nombre por defecto si hace falta
        output_file = f"{title_key}.xml"


    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tei_str)
    # Devolvemos None para indicar que se escribió en disco
    return None


# ==== VALIDACIÓN Y ANÁLISIS DE LOS DOCUMENTOS ====
def count_verses_in_document(main_docx, include_dedication=False):
    """
    Cuenta los versos en un documento DOCX usando la misma lógica que el procesamiento principal.
    
    Args:
        main_docx: Ruta al archivo DOCX
        include_dedication: Si True, cuenta versos desde Titulo_comedia; si False, desde primer Acto
    
    Returns:
        Lista de tuplas (paragraph_index, verse_number, style, text) para cada verso encontrado
    """
    doc = Document(main_docx)
    verses = []
    found_start = False
    verse_counter = 1
    
    for para_idx, para in enumerate(doc.paragraphs):
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""
        
        # Determinar punto de inicio según parámetro
        if not found_start:
            start_style = "Titulo_comedia" if include_dedication else "Acto"
            if style == start_style:
                found_start = True
                if not include_dedication:  # Si empezamos en Acto, reiniciar contador
                    verse_counter = 1
            continue
        
        # Aplicar los mismos filtros que en el procesamiento principal
        if re.match(r'^\$\w+', text):  # Milestones
            continue
        if is_empty_paragraph(para):  # Párrafos vacíos
            continue
        if style in [
            "Personaje", "Acot", "Prosa", 
            "Epigr_Dedic", "Epigr_Dramatis", "Dramatis_lista", "Epigr_final",
            "Acto", "Cita", "Heading 1", "Heading 2", "Heading 3", "Normal"
        ]:
            continue
        
        # Contar versos reales (excluyendo Laguna que no incrementa numeración)
        if style == "Verso":
            verses.append((para_idx, verse_counter, style, text))
            verse_counter += 1
        elif style == "Partido_incial":
            verses.append((para_idx, verse_counter, style, text))
            verse_counter += 1
        elif style in ["Partido_medio", "Partido_final"]:
            # Medio y final usan el número del inicial (counter - 1)
            verses.append((para_idx, verse_counter - 1, style, text))
        elif style == "Laguna":
            # Registrar laguna pero sin incrementar contador
            verses.append((para_idx, verse_counter, style, text))
    
    return verses

def get_verse_number_at_position(main_docx, target_para_index, include_dedication=False):
    """
    Obtiene el número del último verso antes de una posición específica en el documento.
    
    Args:
        main_docx: Ruta al archivo DOCX
        target_para_index: Índice del párrafo objetivo
        include_dedication: Si True, cuenta versos desde Titulo_comedia; si False, desde primer Acto
    
    Returns:
        int: Número del último verso antes de la posición, o 0 si no hay versos previos
    """
    verses = count_verses_in_document(main_docx, include_dedication)
    
    # Buscar el último verso antes de la posición objetivo
    last_verse_number = 0
    for para_idx, verse_number, style, text in verses:
        if para_idx < target_para_index:
            # Solo contar versos que incrementan el contador (no medio/final)
            if style in ["Verso", "Partido_incial"]:
                last_verse_number = verse_number
        else:
            break
    
    return last_verse_number

def is_empty_paragraph(para) -> bool:
    """
    Determina si un párrafo está vacío o solo contiene espacios/caracteres invisibles.
    """
    if not para.text:
        return True
    
    text = para.text.strip()
    if not text:
        return True
    
    # Verificar espacios invisibles, tabulaciones y caracteres especiales
    clean_text = text.replace('\u00A0', '').replace('\t', '').strip()
    if not clean_text:
        return True
    
    # Verificar si todos los runs están vacíos
    if not para.runs or all(not run.text.strip() for run in para.runs):
        return True
    
    # Verificar líneas con solo puntuación, espacios o caracteres de control
    if re.match(r'^[\s\.:!?\(\)"\']+$', text):
        return True
    
    # Verificar líneas con solo caracteres de control o espacios no separables
    if re.match(r'^[\s\u00A0\u2000-\u200F\u2028-\u202F]+$', text):
        return True
    
    return False

def should_skip_paragraph(para, text: str, style: str) -> bool:
    """
    Determina si un párrafo debe ser omitido durante la validación.
    """
    # Párrafos vacíos
    if is_empty_paragraph(para):
        return True
    
    # Milestones que empiezan con '$'
    if re.match(r'^\$\S+', text):
        return True
    
    # Front-matter con asterisco
    if text.startswith("*"):
        return True
    
    # Párrafos dentro de tablas (sinopsis, metadatos, etc.)
    if para._element.xpath("ancestor::w:tbl"):
        return True
    
    return False

def analyze_main_text(main_docx) -> list[str]:
    """
    Analiza el archivo principal y devuelve avisos de párrafos sin estilo
    solo en el cuerpo de la obra (tras Titulo_comedia), ignorando front matter
    y milestones ($.). Incluye dramatis personae pero no cuenta versos.
    """
    warnings: list[str] = []
    unstyled_paragraphs: list[tuple[str, str]] = []  # (text, location_info)

    doc = Document(main_docx)
    found_body = False

    for para_idx, para in enumerate(doc.paragraphs):
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""

        # 1) Buscamos el inicio del body (incluyendo dramatis personae)
        if not found_body:
            if style == "Titulo_comedia":
                found_body = True
            continue

        # 2) Aplicamos los filtros comunes para detectar párrafos problemáticos
        if should_skip_paragraph(para, text, style):
            continue

        # 3) Solo revisamos estilos 'Normal' o None para párrafos sin estilo
        if style in ["Normal", "", None]:
            # Obtener número del último verso antes de esta posición
            last_verse = get_verse_number_at_position(main_docx, para_idx, include_dedication=False)
            
            # Determinar el contexto de localización
            if last_verse > 0:
                location_info = f" (después del verso {last_verse})"
            else:
                # Verificar si estamos antes del primer acto
                verses_with_dedication = count_verses_in_document(main_docx, include_dedication=True)
                has_dedication_verses = any(v[0] < para_idx for v in verses_with_dedication)
                
                if has_dedication_verses:
                    location_info = " (en dramatis personae o dedicatoria)"
                else:
                    location_info = " (al inicio del documento)"
            
            unstyled_paragraphs.append((text, location_info))

    # 4) Tras recorrer todas las líneas, añadimos el warning si hay alguno
    if unstyled_paragraphs:
        count = len(unstyled_paragraphs)
        warnings.append(
            f"⚠️ Se {'ha encontrado' if count == 1 else 'han encontrado'} "
            f"{count} {'línea' if count == 1 else 'líneas'} sin estilo "
            f"en el cuerpo del texto crítico: {main_docx}"
        )
        
        # Añadir detalles de cada párrafo sin estilo
        for i, (text, location) in enumerate(unstyled_paragraphs[:5], 1):  # Mostrar máximo 5
            snippet = text[:60] + "..." if len(text) > 60 else text
            warnings.append(f"   {i}. «{snippet}»{location}")
        
        if len(unstyled_paragraphs) > 5:
            remaining = len(unstyled_paragraphs) - 5
            warnings.append(f"   ... y {remaining} {'línea' if remaining == 1 else 'líneas'} más")

    return warnings




def analyze_notes(
    notes: dict, 
    note_type: str
) -> list[str]:
    """
    Analiza el dict de notas (aparato o nota) y devuelve
    una lista de strings con posibles notas mal formateadas.
    """
    warnings: list[str] = []

    for key, content in notes.items():
        # content es el texto de la nota
        # key puede ser int (verso) o str (palabra)
        text = str(content).strip()
        if not text:
            continue
        # Comprobamos formato: versos "1:..." los quita extract_notes y aquí sólo miramos @palabra
        if isinstance(key, str):
            # en extract_notes mantienes solo claves que cumplían @clave.: no hay invalidas
            continue
        elif isinstance(key, int):
            # en extract_notes mantienes los versos parseados; no hay invalidos
            continue
        else:
            warnings.append(
                f"❌ Nota {note_type} con clave inesperada ({key}): «{text[:60]}»"
            )

    return warnings



def validate_split_verses_impact_on_numbering(main_docx) -> list[str]:
    """
    Valida que los versos partidos incompletos no afecten la numeración total.
    Compara el número esperado de versos completos vs el número real.
    """
    warnings: list[str] = []
    
    # Obtener todos los versos
    verses = count_verses_in_document(main_docx, include_dedication=False)
    
    total_verses = 0  # Versos normales
    split_verse_initials = 0  # Partido_incial (cada uno debería ser un verso)
    split_verse_groups = 0  # Grupos completos de versos partidos (I + [M...] + F)
    incomplete_splits = 0  # Partido_incial sin Partido_final
    
    # Separar por tipo de verso
    verse_sequence = [(style, text) for _, _, style, text in verses]
    
    # 2. Analizar secuencias de versos partidos
    i = 0
    while i < len(verse_sequence):
        style, text = verse_sequence[i]
        
        if style == "Verso":
            total_verses += 1
            i += 1
        elif style == "Partido_incial":
            split_verse_initials += 1
            j = i + 1
            found_final = False
            
            # Buscar el final correspondiente
            while j < len(verse_sequence):
                next_style, _ = verse_sequence[j]
                if next_style == "Partido_final":
                    found_final = True
                    split_verse_groups += 1
                    break
                elif next_style in ["Partido_incial", "Verso"]:
                    break
                j += 1
            
            if not found_final:
                incomplete_splits += 1
            
            i = j + 1 if found_final else i + 1
        else:  # Partido_medio, Partido_final
            i += 1
    
    # 3. Validaciones
    expected_total_verses = total_verses + split_verse_groups
    actual_verse_increments = total_verses + split_verse_initials
    
    if incomplete_splits > 0:
        warnings.append(
            f"⚠️ Se encontraron {incomplete_splits} versos partidos incompletos que pueden "
            f"afectar la numeración automática de versos"
        )
    
    if actual_verse_increments != expected_total_verses:
        diff = actual_verse_increments - expected_total_verses
        warnings.append(
            f"⚠️ Posible desajuste en numeración: se esperan {expected_total_verses} versos "
            f"pero el contador automático generará {actual_verse_increments} "
            f"(diferencia: {diff:+d})"
        )
    
    return warnings

def validate_split_verses(main_docx) -> list[str]:
    """
    Valida que los versos partidos sigan la secuencia lógica correcta:
    - Partido_incial debe tener al menos un Partido_final después
    - Entre Partido_incial y Partido_final puede haber 0 o más Partido_medio
    - No puede haber Partido_medio o Partido_final sin Partido_incial previo
    """
    warnings: list[str] = []
    
    # Obtener todos los versos con su numeración correcta
    verses = count_verses_in_document(main_docx, include_dedication=False)
    
    # 2. Validar secuencia de versos partidos
    i = 0
    while i < len(verses):
        para_idx, verse_num, style, text = verses[i]
        
        if style == "Partido_incial":
            # Buscar el final correspondiente
            j = i + 1
            found_final = False
            middle_count = 0
            
            while j < len(verses):
                next_para_idx, next_verse_num, next_style, next_text = verses[j]
                
                if next_style == "Partido_medio" and next_verse_num == verse_num:
                    middle_count += 1
                elif next_style == "Partido_final" and next_verse_num == verse_num:
                    found_final = True
                    break
                elif next_style in ["Verso", "Partido_incial"]:
                    # Nuevo verso antes de encontrar final
                    break
                j += 1
            
            if not found_final:
                warnings.append(
                    f"❌ Verso partido incompleto: verso {verse_num} '{text[:50]}...' "
                    f"- Falta Partido_final después de Partido_incial"
                )
            
            # Avanzar hasta después del grupo procesado
            i = j + 1 if found_final else i + 1
            
        elif style == "Partido_medio":
            # Partido_medio sin Partido_incial previo
            has_initial = False
            for k in range(i - 1, -1, -1):
                prev_para_idx, prev_verse_num, prev_style, prev_text = verses[k]
                if prev_style == "Partido_incial" and prev_verse_num == verse_num:
                    has_initial = True
                    break
                elif prev_style in ["Verso"] or (prev_style == "Partido_incial" and prev_verse_num != verse_num):
                    break
            
            if not has_initial:
                warnings.append(
                    f"❌ Partido_medio sin inicio: verso {verse_num} '{text[:50]}...' "
                    f"- Partido_medio sin Partido_incial previo"
                )
            i += 1
            
        elif style == "Partido_final":
            # Partido_final sin Partido_incial previo
            has_initial = False
            for k in range(i - 1, -1, -1):
                prev_para_idx, prev_verse_num, prev_style, prev_text = verses[k]
                if prev_style in ["Partido_incial", "Partido_medio"] and prev_verse_num == verse_num:
                    has_initial = True
                    break
                elif prev_style in ["Verso"] or (prev_style in ["Partido_incial", "Partido_final"] and prev_verse_num != verse_num):
                    break
            
            if not has_initial:
                warnings.append(
                    f"❌ Partido_final sin inicio: verso {verse_num} '{text[:50]}...' "
                    f"- Partido_final sin Partido_incial o Partido_medio previo"
                )
            i += 1
            
        else:  # style == "Verso"
            i += 1
    
    return warnings


def validate_Laguna(main_docx) -> list[str]:
    """
    Valida que las lagunas marcadas como Laguna no sean versos específicos perdidos
    que deberían marcarse como Verso normal para mantener la numeración.
    """
    warnings: list[str] = []
    
    doc = Document(main_docx)
    found_body = False
    
    for para_idx, para in enumerate(doc.paragraphs):
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""
        
        # Esperar hasta el inicio del cuerpo principal
        if not found_body:
            if style == "Acto":
                found_body = True
            continue
        
        if style == "Laguna":
            # Obtener el número de verso en la posición actual
            verse_num = get_verse_number_at_position(main_docx, para_idx, include_dedication=False)
            
            # Contar total de versos para contexto
            total_verses = len([v for v in count_verses_in_document(main_docx, include_dedication=False) 
                              if v[2] in ["Verso", "Partido_incial"]])
            
            warnings.append(
                f"⚠️ Has marcado una Laguna tras el verso {verse_num}: '{text[:50]}...' "
                f"- Revisa que no se trate de un verso específico faltante entre corchetes que "
                f"debería contarse en la numeración. La numeración total actual es {total_verses}, "
                f"¿es correcta?"
            )
    
    return warnings


def validate_verso_con_corchetes(main_docx) -> list[str]:
    """
    Valida que los versos marcados como 'Verso' que contienen solo corchetes
    no sean lagunas que deberían marcarse como 'Laguna' para no contar en la numeración.
    """
    warnings: list[str] = []
    
    doc = Document(main_docx)
    found_body = False
    
    # Patrón para detectar texto que consiste principalmente en corchetes con puntos o puntos suspensivos
    import re
    # Incluye tanto puntos normales (.) como puntos suspensivos (…)
    corchetes_pattern = re.compile(r'^\s*\[[\.…]{1,}\]\s*$|^\s*\[\s*[\.…\s]+\s*\]\s*$')
    
    for para_idx, para in enumerate(doc.paragraphs):
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""
        
        # Esperar hasta el inicio del cuerpo principal
        if not found_body:
            if style in ["Titulo_comedia", "Acto"]:
                found_body = True
            continue
        
        if style == "Verso" and corchetes_pattern.match(text):
            # Obtener el número de verso en la posición actual
            verse_num = get_verse_number_at_position(main_docx, para_idx, include_dedication=False)
            
            # Contar total de versos para contexto
            total_verses = len([v for v in count_verses_in_document(main_docx, include_dedication=False) 
                              if v[2] in ["Verso", "Partido_incial"]])
            
            warnings.append(
                f"⚠️ Has marcado como Verso normal una línea con corchetes en el verso {verse_num}: '{text}' "
                f"- ¿Se trata de una laguna incierta que debería marcarse como 'Laguna' para no "
                f"contarla en la numeración? La numeración total actual es {total_verses}, "
                f"¿es correcta considerando este verso?"
            )
    
    return warnings


def validate_documents(main_docx, aparato_docx=None, notas_docx=None) -> list[str]:
    """
    Ejecuta las comprobaciones sobre los DOCX y devuelve una lista
    de strings con los avisos encontrados (vacía si no hay warnings).
    """
    warnings: list[str] = []

    # 1) Comprueba existencia del principal
    if not os.path.exists(main_docx):
        warnings.append(f"❌ No existe el archivo principal: {main_docx}")
        return warnings

    # 2) Validación de estilos en el body
    ESTILOS_VALIDOS = {
        "Titulo_comedia", "Acto", "Prosa", "Verso", "Partido_incial",
        "Partido_medio", "Partido_final", "Personaje", "Acot",
        "Epigr_Dedic", "Epigr_Dramatis", "Dramatis_lista", "Epigr_final",
        "Laguna"  # Nuevo estilo para lagunas de extensión incierta
    }
    SKIP_STYLES = {"Cita", "Heading 1", "Heading 2", "Heading 3"}
    doc = Document(main_docx)
    found_body = False

    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""

        # 2.1) Esperar hasta el inicio de cuerpo
        if not found_body:
            if style in ("Titulo_comedia", "Acto"):
                found_body = True
            continue

        # 2.2) Aplicar filtros comunes para omitir párrafos
        if should_skip_paragraph(para, text, style):
            continue
        
        # 2.3) Omitir estilos específicos que no necesitan validación
        if style in SKIP_STYLES:
            continue

        # 2.4) Validar estilo permitido (solo si no es un párrafo a omitir)
        if style not in ESTILOS_VALIDOS:
            snippet = text[:60]
            warnings.append(f"❌ Estilo no válido: {style or 'None'} — Texto: {snippet}")

    # 3) Análisis avanzado del texto principal (detección de párrafos sin estilo)
    warnings.extend(analyze_main_text(main_docx))

    # 4) Notas de aparato
    if aparato_docx:
        if not os.path.exists(aparato_docx):
            warnings.append(f"❌ El archivo de notas de aparato: {aparato_docx}")
        else:
            aparato_notes = extract_notes_with_italics(aparato_docx)
            warnings.extend(analyze_notes(aparato_notes, "aparato"))

    # 5) Notas
    if notas_docx:
        if not os.path.exists(notas_docx):
            warnings.append(f"❌ El archivo de notas no existe: {notas_docx}")
        else:
            nota_notes = extract_notes_with_italics(notas_docx)
            warnings.extend(analyze_notes(nota_notes, "nota"))

    # 6) Validación de versos partidos
    warnings.extend(validate_split_verses(main_docx))
    warnings.extend(validate_split_verses_impact_on_numbering(main_docx))

    # 7) Validación de lagunas marcadas como Laguna
    warnings.extend(validate_Laguna(main_docx))

    # 8) Validación de versos con corchetes que podrían ser lagunas
    warnings.extend(validate_verso_con_corchetes(main_docx))

    return warnings


