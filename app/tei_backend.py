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

def process_front_paragraphs(paragraphs, footnotes_intro):
    """
    Procesa los párrafos del front-matter, generando el bloque <front> del TEI.
    """
    tei_front = []
    subsection_open = False
    subsection_n = 1
    current_section = None
    paragraph_buffer = []
    head_inserted = False

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

    for i, para in enumerate(paragraphs):
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

        # 🔹 Tablas en la sección "Sinopsis"
            if current_section and "sinopsis" in current_section:
                parent = para._parent
                if hasattr(parent, "tables") and parent.tables:
                    for tbl in parent.tables:
                        tei_front.append(process_table_to_tei(tbl))
            continue

        # 🔹 Añade al buffer
        paragraph_buffer.append(para)

    flush_paragraph_buffer()

    if subsection_open:
        tei_front.append('        </div>')  # cierra la última subsection

    return "\n".join(tei_front)

def process_table_to_tei(table):
    """
    Convierte una tabla DOCX en una tabla TEI.
    """
    ncols = len(table.columns)
    tei = ['<table rend="rules">']

    # 1) Filas título
    hdr = table.rows[0]
    tei.append('  <row>')
    for cell in hdr.cells:
        raw = extract_text_with_italics(cell.paragraphs[0])
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
            raw = extract_text_with_italics(row.cells[0].paragraphs[0])
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
            raw = extract_text_with_italics(cell.paragraphs[0])
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

    # Inserta el contenido de <front>, incluyendo notas introductorias
    tei.append(process_front_paragraphs(front_paragraphs, footnotes_intro))

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

        elif style == "Partido_incial":
            verse_text = text
            if verse_counter in nota_notes:
                verse_text += f'<note subtype="nota" n="{verse_counter}">{nota_notes[verse_counter]}</note>'
            if verse_counter in aparato_notes:
                verse_text += f'<note subtype="aparato" n="{verse_counter}">{aparato_notes[verse_counter]}</note>'
            tei.append(f'            <l part="I" n="{verse_counter}">{verse_text}</l>')
            verse_counter += 1

        elif style == "Partido_medio":
            tei.append(f'            <l part="M">{text}</l>')

        elif style == "Partido_final":
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
def analyze_main_text(main_docx) -> list[str]:
    """
    Analiza el archivo principal y devuelve avisos de párrafos sin estilo
    solo en el cuerpo de la obra (tras Titulo_comedia), ignorando front matter
    y milestones ($.).
    """
    warnings: list[str] = []
    unstyled_paragraphs: list[str] = []

    doc = Document(main_docx)
    found_body = False

    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text = para.text.strip()

        # 1) Buscamos el inicio del body
        if not found_body:
            if style == "Titulo_comedia":
                found_body = True
            continue

        # 2) Ignoramos párrafos vacíos
        if not text:
            continue

        # 3) Solo revisamos estilos 'Normal' o None
        if style in ["Normal", "", None]:
            # Ignora cualquier milestone que empiece con '$'
            if re.match(r'^\$\S+', text):
                continue
            # Ignora líneas que solo contengan puntuación
            if re.match(r'^[\.:!?\(\)"\']+$', text):
                continue
            unstyled_paragraphs.append(text)

    # 4) Tras recorrer todos las líneas, añadimos el warning si hay alguno
    if unstyled_paragraphs:
        count = len(unstyled_paragraphs)
        mensaje = (
            f"⚠️ Se {'ha encontrado' if count == 1 else 'han encontrado'} "
            f"{count} {'línea' if count == 1 else 'líneas'} sin estilo "
            f"en el cuerpo del texto crítico: {main_docx}"
        )
        warnings.append(mensaje)

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
    STILI_VALIDI = {
        "Titulo_comedia", "Acto", "Prosa", "Verso", "Partido_incial",
        "Partido_medio", "Partido_final", "Personaje", "Acot",
        "Epigr_Dedic", "Epigr_Dramatis", "Dramatis_lista"
    }
    SKIP_STYLES = {"Cita", "Heading 1", "Heading 2", "Heading 3"}
    doc = Document(main_docx)
    found_body = False

    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text  = para.text.strip()

        # 2.1) Esperar hasta el inicio de cuerpo
        if not found_body:
            if style in ("Titulo_comedia", "Acto"):
                found_body = True
            continue

        # 2.2) Filtros para no validar ciertos párrafos
        if not text:
            continue
        if re.match(r'^\$\S+', text):             # milestones "$redondilla", etc.
            continue
        if re.match(r'^[\.:!?\(\)"\']+$', text): # solo puntuación
            continue
        if text.startswith("*"):                 # front-matter con asterisco
            continue
        if style in SKIP_STYLES:                 # citas o encabezados
            continue
        # párrafos dentro de tablas (sinopsis, metadatos, etc.)
        if para._element.xpath("ancestor::w:tbl"):
            continue

        # 2.3) Validar estilo permitido
        if style not in STILI_VALIDI:
            snippet = text[:60]
            warnings.append(f"❌ Estilo no válido: {style or 'None'} — Texto: {snippet}")

    # 3) Análisis avanzado del texto principal (detección de "Normal")
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

    return warnings


