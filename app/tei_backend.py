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


# ==== FUNCIONES DE ESCAPE XML ====
def escape_xml(text):
    """
    Escapa caracteres especiales de XML en el texto.
    """
    if not text:
        return text
    # Orden importante: & primero para no escapar los escapes
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


# ==== EXTRACCIÓN Y PROCESAMIENTO DE NOTAS EN EL PRÓLOGO ====
# Funciones para extraer y procesar notas a pie de página del prólogo o introducción.

def extract_intro_footnotes(docx_path):
    """
    Extrae todas las notas a pie de página de un archivo DOCX, preservando cursivas.
    Devuelve un diccionario {id: note_text} con formato TEI (incluyendo <hi rend="italic">).
    """
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    footnote_dict = {}

    with zipfile.ZipFile(docx_path) as docx_zip:
        with docx_zip.open("word/footnotes.xml") as footnote_file:
            root = etree.parse(footnote_file).getroot()

            for note in root.xpath("//w:footnote[not(@w:type='separator')]", namespaces=ns):
                note_id = note.get(qn("w:id"))
                
                # Procesar todos los runs dentro de la nota para detectar cursivas
                full_text = ""
                for run in note.xpath(".//w:r", namespaces=ns):
                    # Verificar si el run tiene formato cursiva
                    is_italic = run.xpath(".//w:i", namespaces=ns) or run.xpath(".//w:iCs", namespaces=ns)
                    
                    # Extraer el texto del run
                    text_elements = run.xpath(".//w:t", namespaces=ns)
                    run_text = "".join(t.text for t in text_elements if t.text is not None)
                    
                    if run_text:
                        if is_italic:
                            # Envolver en cursiva y escapar el contenido
                            full_text += f'<hi rend="italic">{escape_xml(run_text)}</hi>'
                        else:
                            # Escapar el texto normal
                            full_text += escape_xml(run_text)
                
                if full_text.strip():
                    footnote_dict[note_id] = full_text.strip()

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
                # note_text ya viene escapado de extract_intro_footnotes
                text += f'<note type="intro" n="{note_id}">{note_text}</note>'
        else:
            if run.italic:
                # Escapar el texto dentro de la cursiva
                text += f'<hi rend="italic">{escape_xml(run.text)}</hi>'
            else:
                # Escapar el texto normal
                text += escape_xml(run.text)
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
    Mueve los espacios que están dentro de runs cursivos hacia fuera para preservar el formato.
    """
    # Recorre los runs del párrafo y envuelve en <hi rend="italic"> si es cursiva
    text = ""
    for run in para.runs:
        if run.italic:
            # Extrae espacios del principio y final del texto cursivo
            content = run.text
            leading_spaces = ""
            trailing_spaces = ""
            
            # Extrae espacios del principio
            while content.startswith(" ") or content.startswith("\t"):
                leading_spaces += content[0]
                content = content[1:]
            
            # Extrae espacios del final
            while content.endswith(" ") or content.endswith("\t"):
                trailing_spaces = content[-1] + trailing_spaces
                content = content[:-1]
            
            # Solo envuelve en cursiva el contenido sin espacios, escapando caracteres XML
            if content:  # solo si queda contenido después de quitar espacios
                text += leading_spaces + f'<hi rend="italic">{escape_xml(content)}</hi>' + trailing_spaces
            else:  # si solo había espacios, los añade sin cursiva
                text += run.text
        else:
            # Escapar caracteres XML en texto normal
            text += escape_xml(run.text)
    return text.strip()

def uppercase_preserve_tags(text):
    """
    Convierte texto a mayúsculas preservando etiquetas XML.
    Ejemplo: "<hi rend='italic'>palabra</hi>" → "<hi rend='italic'>PALABRA</hi>"
    """
    parts = re.split(r'(<[^>]+>)', text)
    return ''.join(part.upper() if not part.startswith('<') else part for part in parts)

def extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, section):
    """
    Extrae el texto de un párrafo procesando anotaciones (@palabra) y cursivas.
    ESTRATEGIA FINAL: Usar marcadores para cursivas ANTES de procesar anotaciones.
    """
    
    # Función para normalizar palabras
    def normalize_word(word):
        normalized = unicodedata.normalize('NFKD', word)
        normalized = normalized.encode('ASCII', 'ignore').decode('utf-8').lower().strip()
        return normalized
    
    # Crear conjunto de todas las claves
    all_keys = set()
    if nota_notes:
        all_keys.update(nota_notes.keys())
    if aparato_notes:
        all_keys.update(aparato_notes.keys())
    
    # Contador de ocurrencias
    occurrence_counters = annotation_counter.setdefault("_occurrences", {})
    
    # ==== PASO 1: Construir texto plano CON marcadores de cursiva ====
    # Insertar marcadores ANTES de procesar anotaciones
    marked_text = ""
    prev_italic = False
    
    for run in para.runs:
        if not run.text:
            continue
        
        # Detectar cambios en cursiva y agregar marcadores
        if run.italic and not prev_italic:
            marked_text += '<<<ITALIC_START>>>'
        elif not run.italic and prev_italic:
            marked_text += '<<<ITALIC_END>>>'
        
        marked_text += run.text
        prev_italic = run.italic
    
    # Cerrar cursiva si quedó abierta
    if prev_italic:
        marked_text += '<<<ITALIC_END>>>'
    
    # ==== PASO 2: Procesar TODAS las @palabra ====
    # Primero, reemplazar temporalmente los marcadores por placeholders únicos
    # que no interfieran con el regex pero sean fáciles de restaurar
    
    # Usar caracteres Unicode raros como placeholders
    ITALIC_START_PLACEHOLDER = '\u0001'  # SOH (Start of Heading)
    ITALIC_END_PLACEHOLDER = '\u0002'    # STX (Start of Text)
    
    # Reemplazar marcadores por placeholders
    text_with_placeholders = marked_text.replace('<<<ITALIC_START>>>', ITALIC_START_PLACEHOLDER)
    text_with_placeholders = text_with_placeholders.replace('<<<ITALIC_END>>>', ITALIC_END_PLACEHOLDER)
    
    # Procesar @palabra en el texto con placeholders
    # El regex debe ignorar los placeholders Unicode entre @ y la palabra
    def replace_at_word(match):
        placeholders_before = match.group(1) if match.group(1) else ''  # Placeholders entre @ y palabra
        word = match.group(2)  # palabra
        key = normalize_word(word)
        
        if key not in all_keys:
            # Sin notas, solo quitar el @ y mantener placeholders
            return placeholders_before + word
        
        # Obtener índice de ocurrencia
        occurrence_index = occurrence_counters.get(key, 0)
        occurrence_counters[key] = occurrence_index + 1
        
        # Construir las notas
        notes = []
        
        # Notas filológicas
        if key in nota_notes:
            nota_list = nota_notes[key] if isinstance(nota_notes[key], list) else [nota_notes[key]]
            if occurrence_index < len(nota_list):
                content = nota_list[occurrence_index]
                xml_id = f"n_{key}_{section}_{occurrence_index + 1}"
                xml_id = re.sub(r'[^a-zA-Z0-9_]', '', xml_id).lower()
                notes.append(f'<<<NOTE>>><note subtype="nota" xml:id="{xml_id}">{content}</note><<<ENDNOTE>>>')
        
        # Aparato crítico
        if key in aparato_notes:
            aparato_list = aparato_notes[key] if isinstance(aparato_notes[key], list) else [aparato_notes[key]]
            if occurrence_index < len(aparato_list):
                content = aparato_list[occurrence_index]
                xml_id = f"a_{key}_{section}_{occurrence_index + 1}"
                xml_id = re.sub(r'[^a-zA-Z0-9_]', '', xml_id).lower()
                notes.append(f'<<<NOTE>>><note subtype="aparato" xml:id="{xml_id}">{content}</note><<<ENDNOTE>>>')
        
        # Devolver: placeholders + palabra + notas
        return placeholders_before + word + ''.join(notes)
    
    # Regex que captura @ seguido de opcionalmente placeholders, seguido de palabra
    # Grupo 1: placeholders opcionales (\u0001 o \u0002)
    # Grupo 2: palabra alfanumérica
    pattern = r'@([\u0001\u0002]*)(\w+)'
    processed_text = re.sub(pattern, replace_at_word, text_with_placeholders)
    
    # ==== PASO 3: Restaurar marcadores de cursiva ====
    # Convertir placeholders de vuelta a marcadores
    processed_text = processed_text.replace(ITALIC_START_PLACEHOLDER, '<<<ITALIC_START>>>')
    processed_text = processed_text.replace(ITALIC_END_PLACEHOLDER, '<<<ITALIC_END>>>')
    
    # ==== PASO 4: Escapar XML (excepto notas y marcadores) ====
    # Primero separar notas
    parts = re.split(r'(<<<NOTE>>>.*?<<<ENDNOTE>>>)', processed_text, flags=re.DOTALL)
    escaped_parts = []
    for part in parts:
        if part.startswith('<<<NOTE>>>'):
            # Es una nota, solo quitar marcadores
            note_content = part.replace('<<<NOTE>>>', '').replace('<<<ENDNOTE>>>', '')
            escaped_parts.append(f'<<<NOTE>>>{note_content}<<<ENDNOTE>>>')
        else:
            # Es texto, escapar pero preservar marcadores de cursiva
            # Separar por marcadores de cursiva
            italic_parts = re.split(r'(<<<ITALIC_START>>>|<<<ITALIC_END>>>)', part)
            for ip in italic_parts:
                if ip in ['<<<ITALIC_START>>>', '<<<ITALIC_END>>>']:
                    escaped_parts.append(ip)
                else:
                    escaped_parts.append(escape_xml(ip))
    
    processed_text = ''.join(escaped_parts)
    
    # ==== PASO 5: Convertir marcadores a XML ====
    # Primero, limpiar marcadores de notas
    processed_text = processed_text.replace('<<<NOTE>>>', '').replace('<<<ENDNOTE>>>', '')
    
    # Convertir TODOS los marcadores de cursiva a XML (dentro y fuera de notas)
    processed_text = processed_text.replace('<<<ITALIC_START>>>', '<hi rend="italic">')
    processed_text = processed_text.replace('<<<ITALIC_END>>>', '</hi>')
    
    result = processed_text
    
    return result.strip()

def merge_italic_text(text):
    """
    Fusiona SOLO etiquetas cursivas que están completamente pegadas (sin espacios ni contenido entre ellas).
    Versión conservadora para evitar fusiones incorrectas.
    """
    # Busca SOLO etiquetas que están completamente pegadas: </hi><hi rend="italic">
    pattern = re.compile(r'</hi><hi rend="italic">')
    
    # Reemplaza la secuencia </hi><hi rend="italic"> por nada (fusiona las etiquetas)
    result = pattern.sub('', text)
    
    return result

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
    if not characters:
        return ""
    
    # Normalizar el speaker para comparación
    speaker_normalized = speaker.strip().upper()
    
    # 1. Coincidencia exacta (case-insensitive)
    for name, role_id in characters.items():
        if speaker.strip().upper() == name.upper():
            return role_id
    
    # 2. Coincidencia parcial: el speaker está contenido al inicio del nombre completo
    for name, role_id in characters.items():
        name_upper = name.upper()
        # Verificar si el speaker es el primer término (antes de coma)
        if name_upper.startswith(speaker_normalized + ','):
            return role_id
        # O si el speaker coincide con la primera palabra
        first_word = name.split(',')[0].split()[0].upper()
        if speaker_normalized == first_word:
            return role_id
        # O si el speaker coincide con la segunda palabra (para "DON CARLOS")
        words = name.split(',')[0].split()
        if len(words) > 1 and speaker_normalized == words[1].upper():
            return role_id
    
    # 3. Coincidencia difusa (fuzzy matching) como último recurso
    close_matches = get_close_matches(speaker.strip(), characters.keys(), n=1, cutoff=0.6)
    if close_matches:
        return characters[close_matches[0]]

    return ""


# ==== PROCESAMIENTO DE METADATOS Y FRONT-MATTER ====
def parse_metadata_docx(path, header_mode="prolope"):
    """
    Extrae metadatos de un archivo .docx estructurado en tablas y construye un teiHeader TEI/XML.
    
    Args:
        path: Ruta al archivo DOCX de metadatos.
        header_mode: "prolope" para header completo con datos PROLOPE, 
                     "minimo" para header solo con datos del usuario y referencia a la app.
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

    if 'Editor' in main_meta and main_meta['Editor']:
        tei.append(f'      <editor>{main_meta["Editor"]}</editor>')

    if 'Responsable/s revisión' in main_meta and main_meta['Responsable/s revisión']:
        tei.append('      <respStmt>')
        if header_mode == "prolope":
            tei.append('        <resp>Edición crítica digital revisada filológicamente por</resp>')
        else:
            tei.append('        <resp>Responsable/s revisión</resp>')
        for name in main_meta['Responsable/s revisión'].split(','):
            tei.append(f'        <persName>{name.strip()}</persName>')
        tei.append('      </respStmt>')

    if 'Responsable marcado automático' in main_meta and main_meta['Responsable marcado automático']:
        tei.append('      <respStmt>')
        if header_mode == "prolope":
            tei.append('        <resp>Marcado XML-TEI automático revisado por</resp>')
        else:
            tei.append('        <resp>Responsable marcado automático</resp>')
        for name in main_meta['Responsable marcado automático'].split(','):
            tei.append(f'        <persName>{name.strip()}</persName>')
        tei.append('      </respStmt>')

    # Solo en modo PROLOPE: añadir referencia al grupo de investigación
    if header_mode == "prolope":
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
    tei.append('    </publicationStmt>')
    
    # Solo en modo PROLOPE: añadir seriesStmt
    if header_mode == "prolope":
        tei.append('    <seriesStmt>')
        tei.append('      <title>Biblioteca Digital PROLOPE</title>')
        tei.append('      <respStmt>')
        tei.append('        <resp>Dirección de</resp>')
        tei.append('        <persName ref="https://orcid.org/0000-0002-7429-9709"><forename>Ramón</forename> <surname>Valdés Gázquez</surname></persName>')
        tei.append('      </respStmt>')
        tei.append('      <idno type="URI">https://bibdigitalprolope.com/</idno>')
        tei.append('    </seriesStmt>')

    # sourceDesc
    tei.extend(['    <sourceDesc>', '      <biblStruct xml:lang="es">', '        <monogr>'])
    
    # Autor
    if header_mode == "prolope":
        tei.append('          <author>')
        tei.append('            <persName ref="http://datos.bne.es/persona/XX1719671"><forename>Félix Lope</forename><surname>de Vega Carpio</surname></persName>')
        tei.append('          </author>')
    else:
        # Modo mínimo: autor desde metadatos
        tei.append(f'          <author>{main_meta.get("Autor", "")}</author>')
    
    # Títulos
    tei.append(f'          <title type="main">{source_meta.get("Título comedia", "")}</title>')
    if "Subtítulo" in source_meta and source_meta.get("Subtítulo"):
        tei.append(f'          <title type="alt">{source_meta.get("Subtítulo", "")}</title>')
    
    # Título del volumen (si existe)
    if source_meta.get("Título volumen"):
        tei.append(f'          <title level="s">{source_meta.get("Título volumen", "")}</title>')
    
    # Solo en modo PROLOPE: añadir "Parte"
    if header_mode == "prolope" and source_meta.get("Parte"):
        tei.append(f'          <title level="a">Parte {source_meta.get("Parte", "")}</title>')
    
    # Editor (si existe)
    if 'Editor' in main_meta and main_meta['Editor']:
        tei.append(f'          <editor>{main_meta["Editor"]}</editor>')
    
    # Coordinadores del volumen (si existen)
    if 'Coordinadores volumen' in source_meta and source_meta['Coordinadores volumen']:
        tei.append('          <respStmt>')
        if header_mode == "prolope":
            tei.append('            <resp>Coordinación del volumen a cargo de</resp>')
        else:
            tei.append('            <resp>Coordinadores volumen</resp>')
        for name in source_meta['Coordinadores volumen'].split(','):
            tei.append(f'            <persName>{name.strip()}</persName>')
        tei.append('          </respStmt>')
    
    # Solo en modo PROLOPE: añadir availability
    if header_mode == "prolope":
        tei.append('          <availability status="restricted">')
        tei.append('            <p>Todos los derechos reservados.</p>')
        tei.append('          </availability>')
    
    # Imprint
    tei.append('          <imprint>')
    tei.append(f'            <pubPlace>{source_meta.get("Lugar publicación", "")}</pubPlace>')
    tei.append(f'            <publisher>{source_meta.get("Publicado por", "")}</publisher>')
    tei.append(f'            <date>{source_meta.get("Fecha publicación", "")}</date>')
    
    # Volumen y páginas (si existen)
    if source_meta.get("Volumen"):
        tei.append(f'            <biblScope unit="volume" n="{source_meta.get("Volumen", "")}">vol. {source_meta.get("Volumen", "")}</biblScope>')
    if source_meta.get("Páginas"):
        tei.append(f'            <biblScope unit="page">{source_meta.get("Páginas", "")}</biblScope>')
    
    tei.append('          </imprint>')
    tei.append('        </monogr>')
    tei.append('      </biblStruct>')
    tei.append('      <listWit>')
    for siglum, desc in witnesses:
        tei.append(f'        <witness xml:id="{siglum}">')
        tei.append(f'          <label>{desc}</label>')
        tei.append('        </witness>')
    tei.append('      </listWit>')
    tei.append('    </sourceDesc>')
    tei.append('  </fileDesc>')
    tei.append('  <encodingDesc>')
    
    # Solo en modo PROLOPE: añadir editorialDecl
    if header_mode == "prolope":
        tei.append('    <editorialDecl>')
        tei.append('      <p>El texto se transformó desde archivos DOCX mediante un flujo semiautomático con feniX-ML (versión 1.0.0).</p>')
        tei.append('    </editorialDecl>')
    
    # Siempre incluir appInfo (en ambos modos)
    tei.append('    <appInfo>')
    tei.append('      <application ident="feniX-ML" version="1.0.0">')
    tei.append('        <label>feniX-ML</label>')
    if header_mode == "prolope":
        tei.append('        <desc>Conversor de ediciones críticas de teatro del Siglo de Oro de DOCX a XML-TEI, desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde (PROLOPE).</desc>')
        tei.append('        <ref target="https://github.com/prolopeuab/feniX-ML">Repositorio y documentación</ref>')
    else:
        tei.append('        <desc>Conversor de ediciones críticas de DOCX a XML-TEI.</desc>')
        tei.append('        <ref target="https://github.com/prolopeuab/feniX-ML">https://github.com/prolopeuab/feniX-ML</ref>')
    tei.append('      </application>')
    tei.append('    </appInfo>')
    tei.append('  </encodingDesc>')
    tei.append('</teiHeader>')

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
    processed_tables = set()
    tables_processed_in_current_section = False
    in_sp_front = False  # Estado para controlar <sp> en el front

    def flush_paragraph_buffer():
        nonlocal paragraph_buffer, in_sp_front
        for p in paragraph_buffer:
            text = extract_text_with_intro_notes(p, footnotes_intro)
            # Obtener el estilo del párrafo
            style = ""
            if p.style:
                style = p.style.name
            
            if style == "Quote":
                # Cerrar <sp> si está abierto antes de <cit>
                if in_sp_front:
                    tei_front.append('          </sp>')
                    in_sp_front = False
                tei_front.append(f'          <cit rend="blockquote">')
                tei_front.append(f'            <quote>{text}</quote>')
                tei_front.append(f'          </cit>')
            elif style == "Personaje":
                # Cerrar <sp> anterior si existe
                if in_sp_front:
                    tei_front.append('          </sp>')
                # Abrir nuevo <sp> sin atributo who (personajes no declarados aún)
                tei_front.append('          <sp>')
                tei_front.append(f'            <speaker>{text}</speaker>')
                in_sp_front = True
            elif style == "Verso":
                if text.strip():
                    # Los versos van dentro de <sp> si está abierto
                    if in_sp_front:
                        tei_front.append(f'            <l>{text.strip()}</l>')
                    else:
                        tei_front.append(f'          <l>{text.strip()}</l>')
            elif text.strip():
                # Cerrar <sp> si está abierto antes de <p>
                if in_sp_front:
                    tei_front.append('          </sp>')
                    in_sp_front = False
                tei_front.append(f'          <p>{text.strip()}</p>')
        paragraph_buffer.clear()
        # Cerrar <sp> al final del buffer si quedó abierto
        if in_sp_front:
            tei_front.append('          </sp>')
            in_sp_front = False

    def process_tables_for_current_section():
        """Procesa las tablas para la sección actual."""
        nonlocal tables_processed_in_current_section
        if current_section and "sinopsis" in current_section and not tables_processed_in_current_section:
            for table_idx, table in enumerate(doc.tables):
                if table_idx not in processed_tables:
                    tei_front.append(process_table_to_tei(table, footnotes_intro))
                    processed_tables.add(table_idx)
            tables_processed_in_current_section = True

    for i, para in enumerate(front_paragraphs):
        raw = extract_text_with_intro_notes(para, footnotes_intro)
        text = para.text.strip() if para.text else ""
        if not text:
            continue

        # Ignora "Introducción"
        if text.lower() == "introducción":
            continue

        # Gestión del título principal "PRÓLOGO"
        if not head_inserted and "prólogo" in text.lower():
            flush_paragraph_buffer()
            tei_front.append(f'        <head type="divTitle" subtype="MenuLevel_1">PRÓLOGO</head>')
            head_inserted = True
            continue

        # Reconocimiento de subtítulo con almohadilla
        if text.startswith("#"):
            flush_paragraph_buffer()
            # Usar 'raw' que ya tiene las notas procesadas, y quitar el # del texto procesado
            title = raw.lstrip("#").strip()
            if title.lower() == "prólogo":
                continue
            if subsection_open:
                tei_front.append('        </div>')
            tei_front.append(f'        <div type="subsection" n="{subsection_n}">')
            tei_front.append(f'          <head type="divTitle" subtype="MenuLevel_2">{title}</head>')
            subsection_open = True
            current_section = title.lower()
            subsection_n += 1
            tables_processed_in_current_section = False
            continue

        # Añade al buffer
        paragraph_buffer.append(para)

        # Si tenemos párrafos en el buffer y estamos en sinopsis, procesar en orden correcto
        if (current_section and "sinopsis" in current_section and 
            len(paragraph_buffer) > 0 and not tables_processed_in_current_section):
            flush_paragraph_buffer()
            process_tables_for_current_section()

    # Procesar cualquier contenido restante
    flush_paragraph_buffer()
    
    # Procesar tablas que no se hayan procesado aún
    if current_section and "sinopsis" in current_section and not tables_processed_in_current_section:
        process_tables_for_current_section()

    if subsection_open:
        tei_front.append('        </div>')

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

def process_annotations_raw(raw_text, nota_notes, aparato_notes, annotation_counter, section):
    """
    Procesa anotaciones @palabra en texto plano (sin tags XML de cursivas).
    Esta función se ejecuta ANTES de aplicar las cursivas.
    Devuelve el texto con las anotaciones reemplazadas por: palabra<note>...</note>
    """
    # Función para normalizar palabras (sin acentos, minúsculas)
    def normalize_word(word):
        normalized = unicodedata.normalize('NFKD', word)
        normalized = normalized.encode('ASCII', 'ignore').decode('utf-8').lower().strip()
        return normalized
    
    # Crear conjunto de todas las claves normalizadas
    all_keys = set()
    if nota_notes:
        all_keys.update(nota_notes.keys())
    if aparato_notes:
        all_keys.update(aparato_notes.keys())
    
    # Contador de ocurrencias para cada palabra
    occurrence_counters = annotation_counter.setdefault("_occurrences", {})
    
    # Función de reemplazo
    def replace_annotation(match):
        phrase = match.group(1)  # La palabra capturada (sin el @)
        key = normalize_word(phrase)
        
        if key not in all_keys:
            # No hay notas para esta palabra, solo eliminar el @
            return phrase
        
        # Obtener el índice de ocurrencia actual (0-indexed)
        occurrence_index = occurrence_counters.get(key, 0)
        occurrence_counters[key] = occurrence_index + 1
        
        # Construir las notas correspondientes a esta ocurrencia
        note_str = ""
        
        # === NOTAS FILOLÓGICAS ===
        if key in nota_notes:
            nota_list = nota_notes[key]
            if not isinstance(nota_list, list):
                nota_list = [nota_list]
            
            if occurrence_index < len(nota_list):
                content = nota_list[occurrence_index]
                xml_id_nota = f"n_{key}_{section}_{occurrence_index + 1}"
                xml_id_nota = re.sub(r'\s+', '_', xml_id_nota)
                xml_id_nota = re.sub(r'[^a-zA-Z0-9_]', '', xml_id_nota)
                xml_id_nota = xml_id_nota.lower()
                note_str += f'<note subtype="nota" xml:id="{xml_id_nota}">{content}</note>'
        
        # === APARATO CRÍTICO ===
        if key in aparato_notes:
            aparato_list = aparato_notes[key]
            if not isinstance(aparato_list, list):
                aparato_list = [aparato_list]
            
            if occurrence_index < len(aparato_list):
                content = aparato_list[occurrence_index]
                xml_id_aparato = f"a_{key}_{section}_{occurrence_index + 1}"
                xml_id_aparato = re.sub(r'\s+', '_', xml_id_aparato)
                xml_id_aparato = re.sub(r'[^a-zA-Z0-9_]', '', xml_id_aparato)
                xml_id_aparato = xml_id_aparato.lower()
                note_str += f'<note subtype="aparato" xml:id="{xml_id_aparato}">{content}</note>'
        
        # Devolver la palabra (ya escapada XML si fuera necesario) seguida de las notas
        return f'{escape_xml(phrase)}{note_str}'
    
    # Patrón simple: @palabra (sin preocuparnos por cursivas aún)
    processed_text = re.sub(r'@(\w+)', replace_annotation, raw_text)
    
    return processed_text

def extract_notes_with_italics(docx_path: str) -> dict:
    """
    Extrae notas o aparato de un DOCX.
    Devuelve un dict donde las claves pueden ser:
    - int: versos normales (ej: 329)
    - str: palabras normalizadas (ej: "dedicatoria") o versos con sufijo alfabético (ej: "329a", "329b")
    
    Los valores son SIEMPRE LISTAS de strings (para manejar múltiples notas secuencialmente).
    
    SUFIJOS ALFABÉTICOS PARA VERSOS PARTIDOS:
    - Los versos partidos usan sufijos: 329a (primera parte), 329b (segunda parte), etc.
    - El sufijo se asigna secuencialmente según el orden de las partes
    - Ejemplo: verso con 3 partes tendría "329a:", "329b:", "329c:" en el archivo de notas
    - Funciona para cualquier número de partes (a-z soporta hasta 26 partes)
    
    FORMATO EN ARCHIVO DE NOTAS:
    - Verso normal: "329: contenido de la nota"
    - Verso partido parte 1: "329a: contenido de la nota"
    - Verso partido parte 2: "329b: contenido de la nota"
    - Palabra: "@dedicatoria: contenido de la nota"
    """
    notes: dict = {}
    if not docx_path or not os.path.exists(docx_path):
        return notes

    def normalize_key(word):
        """Normaliza una palabra eliminando acentos y convirtiendo a minúsculas."""
        # Descomponer caracteres con acentos
        normalized = unicodedata.normalize('NFKD', word)
        # Eliminar marcas diacríticas y convertir a minúsculas
        normalized = normalized.encode('ASCII', 'ignore').decode('utf-8').lower().strip()
        return normalized

    doc = Document(docx_path)
    for para in doc.paragraphs:
        text = extract_text_with_italics(para).strip()

        # Notas tipo verso: "1: contenido" o "329a: contenido" (con sufijo alfabético)
        # El sufijo alfabético se usa para versos partidos: 329a, 329b, 329c, etc.
        match_verse = re.match(r'^(\d+[a-z]?):\s*(.*)', text)
        # Notas tipo @palabra: "@palabra: contenido"
        match_single = re.match(r'^@([^@]+?):\s*(.*)', text)

        if match_verse:
            verse_key = match_verse.group(1)  # Puede ser "329" o "329a"
            content = match_verse.group(2).strip()
            
            # Si tiene sufijo alfabético, usar como string; si no, convertir a int
            if re.match(r'^\d+[a-z]$', verse_key):
                # Tiene sufijo: usar string como clave (ej: "329a")
                key = verse_key
            else:
                # Sin sufijo: convertir a int para retrocompatibilidad
                key = int(verse_key)
            
            # Siempre usar listas para facilitar el acceso secuencial
            if key not in notes:
                notes[key] = []
            notes[key].append(content)
                
        elif match_single:
            key_original = match_single.group(1).strip()
            content = match_single.group(2).strip()
            
            # Normalizar la clave para insensibilidad a mayúsculas/acentos
            key = normalize_key(key_original)
            
            # Siempre usar listas para facilitar el acceso secuencial
            if key not in notes:
                notes[key] = []
            notes[key].append(content)

    return notes


# ==== PROCESAMIENTO DE NOTAS Y APARATO ====

def process_annotations_with_ids(text, nota_notes, aparato_notes, annotation_counter, section):
    """
    Sustituye marcadores @palabra en el texto por notas TEI con xml:ids únicos.
    Usa sincronización secuencial: la 1ª ocurrencia de @palabra recibe la 1ª nota,
    la 2ª ocurrencia recibe la 2ª nota, etc.
    
    - nota_notes y aparato_notes son dicts con claves YA NORMALIZADAS y valores como LISTAS.
    - annotation_counter lleva el conteo de ocurrencias de cada palabra por sección.
    - section es el nombre de la sección (p.ej. 'p', 'speaker', etc.).
    """
    if not text:
        return ""

    # Aseguramos dicts válidos
    nota_notes = nota_notes or {}
    aparato_notes = aparato_notes or {}

    # Función de normalización para palabras del texto (debe coincidir con extract_notes_with_italics)
    def normalize_word(word):
        if isinstance(word, int):
            return word
        # Quitamos tags <hi> y descomponemos acentos
        plain = re.sub(r'<hi rend="italic">(.*?)</hi>', r'\1', word)
        normalized = unicodedata.normalize('NFKD', plain)
        normalized = normalized.encode('ASCII', 'ignore').decode('utf-8').lower().strip()
        return normalized

    # Las claves de las notas ya vienen normalizadas, no necesitamos procesarlas de nuevo
    # Solo necesitamos combinar los dicts
    all_keys = set(nota_notes.keys()) | set(aparato_notes.keys())

    new_text = text.strip()
    
    # Contador global de ocurrencias (necesita ser accesible desde la función de reemplazo)
    occurrence_counters = annotation_counter.setdefault("_occurrences", {})
    
    # Función de reemplazo para usar con re.sub
    def replace_annotation(match):
        # Determinar qué patrón coincidió y extraer la palabra
        phrase = match.group(1)  # Siempre está en el primer grupo de captura
        full_match = match.group(0)  # El match completo
        
        # Determinar si la palabra debe estar en cursiva
        # Casos con cursiva: @<hi rend="italic">palabra</hi> o <hi rend="italic">@palabra</hi>
        in_italic = '<hi rend="italic">' in full_match
        
        key = normalize_word(phrase)
        
        if key not in all_keys:
            # No hay notas para esta palabra, solo eliminar el @ y mantener cursiva si la tenía
            if in_italic:
                return f'<hi rend="italic">{phrase}</hi>'
            else:
                return phrase
        
        # Obtener el índice de ocurrencia actual (0-indexed)
        occurrence_index = occurrence_counters.get(key, 0)
        occurrence_counters[key] = occurrence_index + 1
        
        # Construir las notas correspondientes a esta ocurrencia
        note_str = ""
        
        # === NOTAS FILOLÓGICAS ===
        if key in nota_notes:
            nota_list = nota_notes[key]
            if not isinstance(nota_list, list):
                nota_list = [nota_list]
            
            if occurrence_index < len(nota_list):
                content = nota_list[occurrence_index]
                xml_id_nota = f"n_{key}_{section}_{occurrence_index + 1}"
                xml_id_nota = re.sub(r'\s+', '_', xml_id_nota)
                xml_id_nota = re.sub(r'[^a-zA-Z0-9_]', '', xml_id_nota)
                xml_id_nota = xml_id_nota.lower()
                note_str += f'<note subtype="nota" xml:id="{xml_id_nota}">{content}</note>'
        
        # === APARATO CRÍTICO ===
        if key in aparato_notes:
            aparato_list = aparato_notes[key]
            if not isinstance(aparato_list, list):
                aparato_list = [aparato_list]
            
            if occurrence_index < len(aparato_list):
                content = aparato_list[occurrence_index]
                xml_id_aparato = f"a_{key}_{section}_{occurrence_index + 1}"
                xml_id_aparato = re.sub(r'\s+', '_', xml_id_aparato)
                xml_id_aparato = re.sub(r'[^a-zA-Z0-9_]', '', xml_id_aparato)
                xml_id_aparato = xml_id_aparato.lower()
                note_str += f'<note subtype="aparato" xml:id="{xml_id_aparato}">{content}</note>'
        
        # Reconstruir el texto con la nota, manteniendo cursiva si la tenía
        if in_italic:
            return f'<hi rend="italic">{phrase}</hi>{note_str}'
        else:
            return f'{phrase}{note_str}'
    
    # Aplicar el reemplazo en múltiples pasadas para capturar todas las variantes:
    # Pasada 1: @<hi rend="italic">palabra</hi> (@ fuera, palabra dentro)
    def replace_at_before_hi(match):
        return replace_annotation(match)
    
    new_text = re.sub(r'@<hi rend="italic">(\w+)</hi>', replace_at_before_hi, new_text)
    
    # Pasada 2: <hi rend="italic">@palabra</hi> (ambos dentro)
    def replace_at_inside_hi(match):
        return replace_annotation(match)
    
    new_text = re.sub(r'<hi rend="italic">@(\w+)</hi>', replace_at_inside_hi, new_text)
    
    # Pasada 3: @palabra (sin cursivas o @ antes de otros elementos)
    def replace_plain_at(match):
        return replace_annotation(match)
    
    new_text = re.sub(r'@(\w+)', replace_plain_at, new_text)

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
    save: bool = True,
    header_mode: str = "prolope"
) -> Optional[str]:
    """
    Convierte uno o más DOCX a un XML-TEI completo.
    
    Args:
        main_docx: Ruta al archivo DOCX principal.
        notas_docx: Ruta al archivo DOCX con notas (opcional).
        aparato_docx: Ruta al archivo DOCX con aparato crítico (opcional).
        metadata_docx: Ruta al archivo DOCX con metadatos (opcional).
        tei_header: Header TEI personalizado (opcional).
        output_file: Ruta donde guardar el archivo TEI (opcional).
        save: Si se debe guardar el archivo (por defecto True).
        header_mode: "prolope" para header completo, "minimo" para header básico.
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
            tei_header = parse_metadata_docx(metadata_docx, header_mode=header_mode)
        except Exception as e:
            raise RuntimeError(f"No se pudo parsear metadata DOCX '{metadata_docx}': {e}")
    elif not tei_header:
        # Cabecera mínima de reserva
        tei_header_respaldo = "<teiHeader>…</teiHeader>"

    header = tei_header if tei_header else tei_header_respaldo

    # Carga del DOCX principal
    try:
        doc = Document(main_docx)
    except Exception as e:
        raise RuntimeError(f"Error al abrir el archivo DOCX principal '{main_docx}': {e}")

    # --- SEPARACIÓN FRONT/BODY BASADA EN 'Titulo_comedia' ---

    # 1) Buscar todos los párrafos con estilo 'Titulo_comedia' (máximo 2: título y subtítulo)
    title_paragraphs = []
    for i, p in enumerate(doc.paragraphs):
        if p.style and p.style.name == "Titulo_comedia":
            title_paragraphs.append(i)
            # Solo nos interesan los primeros 2 consecutivos
            if len(title_paragraphs) == 2:
                break
        elif title_paragraphs:
            # Si ya encontramos al menos uno y este no tiene el estilo, paramos
            break
    
    if not title_paragraphs:
        raise RuntimeError("No se encontró ningún párrafo con estilo 'Titulo_comedia' en el documento")

    title_idx = title_paragraphs[0]
    subtitle_idx = title_paragraphs[1] if len(title_paragraphs) > 1 else None

    # 2) Divide la lista de párrafos en front y body
    # El body comienza después del título (y subtítulo si existe)
    body_start_idx = (subtitle_idx + 1) if subtitle_idx is not None else (title_idx + 1)
    front_paragraphs = list(doc.paragraphs[:title_idx])
    body_paragraphs  = list(doc.paragraphs[body_start_idx:])

    # --- Extracción del título ---
    raw_title = doc.paragraphs[title_idx].text.strip()
    # Generar la clave/slug a partir del título (sin marcadores @)
    clean_title_for_filename = re.sub(r'@', '', raw_title)
    title_key = generate_filename(clean_title_for_filename)


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
    
    # El diccionario de personajes se llenará durante el procesamiento
    characters = {}
    
    act_counter = 0
    verse_counter = 1
    current_milestone = None   # ← inicializado aquí

    # Título procesado con el mismo contador de anotaciones
    title_para = doc.paragraphs[title_idx]
    processed_title = extract_text_with_italics_and_annotations(
        title_para,
        nota_notes,
        aparato_notes,
        annotation_counter,
        "head"
    )

    # Subtítulo procesado (si existe)
    processed_subtitle = None
    if subtitle_idx is not None:
        subtitle_para = doc.paragraphs[subtitle_idx]
        processed_subtitle = extract_text_with_italics_and_annotations(
            subtitle_para,
            nota_notes,
            aparato_notes,
            annotation_counter,
            "head"
        )

    # Notas introductorias
    footnotes_intro = extract_intro_footnotes(main_docx)


    # --- Construcción de <front> y apertura de <body> ---
    tei = [
        '<?xml version="1.0" encoding="UTF-8"?>',  # línea XML
        '<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" '
        'schematypens="http://relaxng.org/ns/structure/1.0"?>',
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
        header,                       # ya generado arriba
        '  <text>',
        '    <front xml:id="front">',
        '      <div type="Introducción" xml:id="prologo">'
    ]

    # Inserta el contenido de <front>, incluyendo notas introductorias y tablas
    tei.append(process_front_paragraphs_with_tables(doc, front_paragraphs, footnotes_intro))

    # Cerramos el front y abrimos el body con el título principal (y subtítulo si existe)
    tei.extend([
        '      </div>',    # cierra <div type="Introducción">
        '    </front>',
        '    <body xml:id="body">',
        '      <div type="Texto" subtype="TEXTO" xml:id="comedia">',
        f'        <head type="mainTitle" xml:id="titulo">{processed_title}</head>',
    ])
    
    # Añadir subtítulo si existe
    if processed_subtitle:
        tei.append(f'        <head type="subTitle">{processed_subtitle}</head>')


    # Recorre todos los párrafos del cuerpo para identificar y procesar cada bloque estilístico
    for para in body_paragraphs:
        style = para.style.name if para.style else "Normal"
        
        # Para detección de milestones, usamos texto simple
        text_simple = para.text.strip()
        
        # 1) Detección de estrofas marcadas con $nombreMilestone
        milestone_match = re.match(r'^\$(\w+)', text_simple)
        if milestone_match:
            current_milestone = milestone_match.group(1)
            continue  # saltamos el resto: sólo guardamos el tipo de estrofa

        # 2) Antes de abrir un nuevo bloque estilístico, cerramos los que estén abiertos
        if style in ["Epigr_Dramatis", "Acto", "Epigr_Dedic"]:
            close_current_blocks(tei, state)


        if style == "Epigr_Dedic":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "head")
            tei.append('        <div type="dedicatoria" xml:id="dedicatoria">')
            tei.append(f'          <head>{processed_text}</head>')
            state["in_dedicatoria"] = True

        elif style == "Epigr_Dramatis":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "head")
            tei.append('        <div type="castList" xml:id="personajes">')
            tei.append(f'            <head>{processed_text}</head>')
            tei.append('          <castList>')
            state["in_cast_list"] = True


        elif style == "Dramatis_lista":
            processed_role_name = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "role")
            role_name = para.text.strip()  # Para el ID usamos el texto sin procesar
            if role_name:
                # Eliminar @ para el nombre limpio
                role_name_clean = re.sub(r'@', '', role_name)
                role_id = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_-]+', '_', role_name_clean)
                tei.append(f'            <castItem><role xml:id="{role_id}">{processed_role_name}</role></castItem>')
                # Llenar el diccionario de personajes aquí
                characters[role_name_clean] = role_id

        elif style == "Acto":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "head")
            # Convertir a mayúsculas para mantener consistencia visual
            processed_text_upper = processed_text.upper()
            act_counter += 1
            tei.append(f'        <div type="subsection" subtype="ACTO" n="{act_counter}" xml:id="acto{act_counter}">')
            tei.append(f'          <head type="acto">{processed_text_upper}</head>')
            state["in_act"] = True

        elif style == "Prosa":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "p")
            if processed_text.strip():
                tei.append(f'          <p>{processed_text}</p>')

        elif style == "Verso":
            if state["in_dedicatoria"]:
                processed_verse = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "l")
                tei.append(f'          <l>{processed_verse}</l>')
            elif state["in_sp"]:
                if current_milestone:
                    tei.append(f'            <milestone unit="stanza" type="{current_milestone}"/>')
                    current_milestone = None
                verse_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "l")
                
                # Procesar notas
                if verse_counter in nota_notes:
                    note_list = nota_notes[verse_counter]
                    # note_list siempre es una lista
                    for i, content in enumerate(note_list, 1):
                        verse_text += f'<note subtype="nota" n="{verse_counter}" xml:id="nota_{verse_counter}_{i}">{content}</note>'
                
                # Mismo tratamiento para aparato
                if verse_counter in aparato_notes:
                    aparato_list = aparato_notes[verse_counter]
                    # aparato_list siempre es una lista
                    for i, content in enumerate(aparato_list, 1):
                        verse_text += f'<note subtype="aparato" n="{verse_counter}" xml:id="aparato_{verse_counter}_{i}">{content}</note>'
                
                tei.append(f'            <l n="{verse_counter}">{verse_text}</l>')
                verse_counter += 1

        elif style == "Laguna":
            # Laguna de extensión incierta - no incrementa el contador de versos
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "gap")
            if state["in_sp"]:
                if current_milestone:
                    tei.append(f'            <milestone unit="stanza" type="{current_milestone}"/>')
                    current_milestone = None
                tei.append(f'            <gap>{processed_text}</gap>')
            elif state["in_dedicatoria"]:
                tei.append(f'          <gap>{processed_text}</gap>')

        elif style == "Partido_inicial":
            # Iniciar verso partido con sistema de sufijos alfabéticos
            # El sufijo 'a' se asigna a la primera parte, 'b' a la segunda, etc.
            if not hasattr(state, "pending_split_verse"):
                state["pending_split_verse"] = {}
            
            verse_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "l")
            text_simple = para.text.strip()
            
            # Inicializar estado del verso partido
            state["current_split_verse"] = verse_counter
            state["split_verse_part_index"] = 0
            
            # Calcular sufijo alfabético para esta parte (primera parte = 'a')
            letra = chr(97 + state["split_verse_part_index"])  # 97 = 'a' en ASCII
            verse_key_with_suffix = f"{verse_counter}{letra}"
            
            state["pending_split_verse"] = {
                "verse_number": verse_counter,
                "initial_text": text_simple,
                "parts": [text_simple],
                "has_notes": verse_counter in nota_notes or verse_counter in aparato_notes or verse_key_with_suffix in nota_notes or verse_key_with_suffix in aparato_notes
            }
            
            # Procesar notas con clave que incluye sufijo (ej: "329a")
            # Buscar primero con sufijo, luego sin sufijo para retrocompatibilidad
            if verse_key_with_suffix in nota_notes:
                note_list = nota_notes[verse_key_with_suffix]
                for i, content in enumerate(note_list, 1):
                    verse_text += f'<note subtype="nota" n="{verse_key_with_suffix}" xml:id="nota_{verse_counter}{letra}_{i}">{content}</note>'
            elif verse_counter in nota_notes:
                # Retrocompatibilidad: buscar sin sufijo
                note_list = nota_notes[verse_counter]
                for i, content in enumerate(note_list, 1):
                    verse_text += f'<note subtype="nota" n="{verse_key_with_suffix}" xml:id="nota_{verse_counter}{letra}_{i}">{content}</note>'
            
            # Mismo tratamiento para aparato
            if verse_key_with_suffix in aparato_notes:
                aparato_list = aparato_notes[verse_key_with_suffix]
                for i, content in enumerate(aparato_list, 1):
                    verse_text += f'<note subtype="aparato" n="{verse_key_with_suffix}" xml:id="aparato_{verse_counter}{letra}_{i}">{content}</note>'
            elif verse_counter in aparato_notes:
                # Retrocompatibilidad: buscar sin sufijo
                aparato_list = aparato_notes[verse_counter]
                for i, content in enumerate(aparato_list, 1):
                    verse_text += f'<note subtype="aparato" n="{verse_key_with_suffix}" xml:id="aparato_{verse_counter}{letra}_{i}">{content}</note>'
            
            # Incrementar índice de parte para la siguiente parte del verso
            state["split_verse_part_index"] += 1
            
            tei.append(f'            <l part="I" n="{verse_key_with_suffix}">{verse_text}</l>')
            verse_counter += 1

        elif style == "Partido_medio":
            # Procesar parte media del verso partido con sufijo alfabético
            text_simple = para.text.strip()
            verse_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "l")
            
            # Recuperar número base del verso partido
            if state.get("current_split_verse") is not None:
                base_verse = state["current_split_verse"]
                part_index = state.get("split_verse_part_index", 1)
            else:
                # Fallback: si no hay estado, usar verso anterior
                print(f"⚠️ Advertencia: Partido_medio sin Partido_inicial previo")
                base_verse = verse_counter - 1
                part_index = 1
            
            # Calcular sufijo alfabético para esta parte (segunda parte = 'b', tercera = 'c', etc.)
            letra = chr(97 + part_index)  # 97 = 'a' en ASCII
            verse_key_with_suffix = f"{base_verse}{letra}"
            
            if hasattr(state, "pending_split_verse") and state.get("pending_split_verse"):
                state["pending_split_verse"]["parts"].append(text_simple)
            
            # Procesar notas con clave que incluye sufijo (ej: "329b", "329c")
            if verse_key_with_suffix in nota_notes:
                note_list = nota_notes[verse_key_with_suffix]
                for i, content in enumerate(note_list, 1):
                    verse_text += f'<note subtype="nota" n="{verse_key_with_suffix}" xml:id="nota_{base_verse}{letra}_{i}">{content}</note>'
            
            if verse_key_with_suffix in aparato_notes:
                aparato_list = aparato_notes[verse_key_with_suffix]
                for i, content in enumerate(aparato_list, 1):
                    verse_text += f'<note subtype="aparato" n="{verse_key_with_suffix}" xml:id="aparato_{base_verse}{letra}_{i}">{content}</note>'
            
            # Incrementar índice de parte para la siguiente parte
            if "split_verse_part_index" in state:
                state["split_verse_part_index"] += 1
            
            tei.append(f'            <l part="M" n="{verse_key_with_suffix}">{verse_text}</l>')

        elif style == "Partido_final":
            # Completar el verso partido con sufijo alfabético y limpiar estado
            text_simple = para.text.strip()
            verse_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "l")
            
            # Recuperar número base del verso partido
            if state.get("current_split_verse") is not None:
                base_verse = state["current_split_verse"]
                part_index = state.get("split_verse_part_index", 1)
            else:
                # Fallback: si no hay estado, usar verso anterior
                print(f"⚠️ Advertencia: Partido_final sin Partido_inicial previo")
                base_verse = verse_counter - 1
                part_index = 1
            
            # Calcular sufijo alfabético para esta parte final
            letra = chr(97 + part_index)  # 97 = 'a' en ASCII
            verse_key_with_suffix = f"{base_verse}{letra}"
            
            if hasattr(state, "pending_split_verse") and state.get("pending_split_verse"):
                state["pending_split_verse"]["parts"].append(text_simple)
                # El verso partido está completo, limpiar estado
                state["pending_split_verse"] = None
            
            # Procesar notas con clave que incluye sufijo (ej: "329c", "329d")
            if verse_key_with_suffix in nota_notes:
                note_list = nota_notes[verse_key_with_suffix]
                for i, content in enumerate(note_list, 1):
                    verse_text += f'<note subtype="nota" n="{verse_key_with_suffix}" xml:id="nota_{base_verse}{letra}_{i}">{content}</note>'
            
            if verse_key_with_suffix in aparato_notes:
                aparato_list = aparato_notes[verse_key_with_suffix]
                for i, content in enumerate(aparato_list, 1):
                    verse_text += f'<note subtype="aparato" n="{verse_key_with_suffix}" xml:id="aparato_{base_verse}{letra}_{i}">{content}</note>'
            
            # Limpiar estado del verso partido
            state["current_split_verse"] = None
            state["split_verse_part_index"] = None
            
            tei.append(f'            <l part="F" n="{verse_key_with_suffix}">{verse_text}</l>')

        elif style == "Acot":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "stage")
            if state["in_sp"]:
                # Si estamos dentro de un <sp>, insertar el <stage> dentro con la misma indentación que <l>
                tei.append(f'            <stage>{processed_text}</stage>')
            else:
                # Si no hay <sp> abierto, insertar <stage> standalone
                tei.append(f'        <stage>{processed_text}</stage>')

        elif style == "Personaje":
            text_simple = para.text.strip()
            who_id = find_who_id(text_simple, characters)
            processed = extract_text_with_italics_and_annotations(
                para, nota_notes, aparato_notes, annotation_counter, "speaker"
            )

            # Cierra <sp> anterior si es necesario
            if state["in_sp"]:
                tei.append('        </sp>')
                state["in_sp"] = False

            # Abrir <sp> con who si está disponible
            if who_id:
                tei.append(f'        <sp who="#{who_id}">')
            else:
                # No hay who_id (personaje no encontrado en dramatis personae)
                tei.append('        <sp>')
            
            # SIEMPRE insertar <speaker> en cada nuevo <sp>
            # Cada intervención es un <sp> separado y debe tener su propio <speaker>
            # Convertir speaker a mayúsculas, preservando etiquetas XML
            processed_upper = uppercase_preserve_tags(processed)
            tei.append(f'          <speaker>{processed_upper}</speaker>')
            
            state["in_sp"] = True

        elif style == "Prosa":
            # Párrafos en prosa, pueden estar en dedicatoria o en otras secciones
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "p")
            if state["in_dedicatoria"]:
                tei.append(f'          <p>{processed_text}</p>')
            elif state["in_cast_list"]:
                tei.append(f'            <p>{processed_text}</p>')
            elif state["in_sp"]:
                tei.append(f'            <p>{processed_text}</p>')
            else:
                # Prosa en contexto general
                tei.append(f'        <p>{processed_text}</p>')

        elif style == "Epigr_final":
            processed_text = extract_text_with_italics_and_annotations(para, nota_notes, aparato_notes, annotation_counter, "trailer")
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
        elif style == "Partido_inicial":
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
            if style in ["Verso", "Partido_inicial"]:
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

    # Front-matter con almohadilla (títulos de sección del prólogo)
    if text.startswith("#"):
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
    last_act_name = None

    for para_idx, para in enumerate(doc.paragraphs):
        style = para.style.name if para.style else ""
        text = para.text.strip() if para.text else ""

        # 1) Buscamos el inicio del body (incluyendo dramatis personae)
        if not found_body:
            if style == "Titulo_comedia":
                found_body = True
            continue

        # Registrar actos para determinar ubicación
        if style == "Acto":
            last_act_name = text

        # 2) Aplicamos los filtros comunes para detectar párrafos problemáticos
        if should_skip_paragraph(para, text, style):
            continue

        # 3) Solo revisamos estilos 'Normal' o None para párrafos sin estilo
        if style in ["Normal", "", None]:
            # Obtener número del último verso antes de esta posición
            last_verse = get_verse_number_at_position(main_docx, para_idx, include_dedication=False)
            
            # Determinar el contexto de localización
            if last_verse > 0:
                # Hay versos antes, está dentro de un acto
                location_info = f" (después del verso {last_verse})"
            elif last_act_name:
                # Hay un acto definido pero aún no hay versos
                location_info = f" (en {last_act_name}, antes del primer verso marcado)"
            else:
                # Está antes del primer acto (en dramatis personae o dedicatoria)
                location_info = " (en dramatis personae o dedicatoria)"
            
            unstyled_paragraphs.append((text, location_info))

    # 4) Tras recorrer todas las líneas, añadimos el warning si hay alguno
    if unstyled_paragraphs:
        count = len(unstyled_paragraphs)
        warnings.append(
            f"❌ LÍNEAS SIN ESTILO DETECTADAS ({count})\n"
            f"   Archivo: {os.path.basename(main_docx)}\n"
            f"   Revisa que todas las líneas tengan el estilo correcto aplicado."
        )
        
        # Añadir detalles de cada párrafo sin estilo (mostrar máximo 5)
        for i, (text, location) in enumerate(unstyled_paragraphs[:5], 1):
            snippet = text[:60] + "..." if len(text) > 60 else text
            warnings.append(f"   {i}. «{snippet}»{location}")
        
        if len(unstyled_paragraphs) > 5:
            remaining = len(unstyled_paragraphs) - 5
            warnings.append(f"   ... y {remaining} {'línea más' if remaining == 1 else 'líneas más'}")

    return warnings




def analyze_notes(
    notes: dict, 
    note_type: str
) -> list[str]:
    """
    Analiza el dict de notas (aparato o nota) y devuelve
    una lista de strings con posibles notas mal formateadas o múltiples.
    """
    warnings: list[str] = []

    for key, content in notes.items():
        # key puede ser int (verso) o str (palabra normalizada)
        
        # Verificar si hay múltiples notas para la misma clave
        if isinstance(content, list) and len(content) > 1:
            if isinstance(key, str):
                # Notas @palabra con múltiples entradas
                warnings.append(
                    f"⚠️ MÚLTIPLES {note_type.upper()}S PARA '@{key}' ({len(content)})\n"
                    f"   Verifica que la asignación secuencial en el texto sea correcta."
                )
            elif isinstance(key, int):
                # Notas de verso con múltiples entradas
                warnings.append(
                    f"⚠️ MÚLTIPLES {note_type.upper()}S PARA VERSO {key} ({len(content)})\n"
                    f"   Verifica que todas las {note_type}s sean correctas."
                )
        
        # Validar que el contenido no esté vacío
        if isinstance(content, list):
            for i, text in enumerate(content, 1):
                if not text.strip():
                    if isinstance(key, str):
                        warnings.append(f"❌ {note_type.capitalize()} vacía: '@{key}' (entrada #{i})")
                    elif isinstance(key, int):
                        warnings.append(f"❌ {note_type.capitalize()} vacía: verso {key} (entrada #{i})")
        elif not str(content).strip():
            # Caso de contenido no-lista (por compatibilidad)
            if isinstance(key, str):
                warnings.append(f"❌ {note_type.capitalize()} vacía: '@{key}'")
            elif isinstance(key, int):
                warnings.append(f"❌ {note_type.capitalize()} vacía: verso {key}")

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
    split_verse_initials = 0  # Partido_inicial (cada uno debería ser un verso)
    split_verse_groups = 0  # Grupos completos de versos partidos (I + [M...] + F)
    incomplete_splits = 0  # Partido_inicial sin Partido_final
    
    # Separar por tipo de verso
    verse_sequence = [(style, text) for _, _, style, text in verses]
    
    # 2. Analizar secuencias de versos partidos
    i = 0
    while i < len(verse_sequence):
        style, text = verse_sequence[i]
        
        if style == "Verso":
            total_verses += 1
            i += 1
        elif style == "Partido_inicial":
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
                elif next_style in ["Partido_inicial", "Verso"]:
                    break
                j += 1
            
            if not found_final:
                incomplete_splits += 1
            
            i = j + 1 if found_final else i + 1
        else:  # Partido_medio, Partido_final
            i += 1
    
    # 3. Validaciones - Solo mostrar desajuste si existe
    expected_total_verses = total_verses + split_verse_groups
    actual_verse_increments = total_verses + split_verse_initials
    
    if actual_verse_increments != expected_total_verses:
        diff = actual_verse_increments - expected_total_verses
        plural_s = 's' if abs(diff) > 1 else ''
        warnings.append(
            f"\n⚠️ DESAJUSTE EN LA NUMERACIÓN DE VERSOS\n"
            f"Se esperan {expected_total_verses} pero se numerarán {actual_verse_increments}. "
            f"Hay una diferencia de {diff:+d} verso{plural_s} debido a versos partidos incompletos."
        )
    
    return warnings

def validate_split_verses(main_docx) -> list[str]:
    """
    Valida que los versos partidos sigan la secuencia lógica correcta:
    - Partido_inicial debe tener al menos un Partido_final después
    - Entre Partido_inicial y Partido_final puede haber 0 o más Partido_medio
    - No puede haber Partido_medio o Partido_final sin Partido_inicial previo
    """
    warnings: list[str] = []
    verse_problems: list[tuple[int, str, str]] = []  # (verse_num, text, problem_description)
    
    # Obtener todos los versos con su numeración correcta
    verses = count_verses_in_document(main_docx, include_dedication=False)
    
    # 2. Validar secuencia de versos partidos y recopilar problemas
    i = 0
    while i < len(verses):
        para_idx, verse_num, style, text = verses[i]
        
        if style == "Partido_inicial":
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
                elif next_style in ["Verso", "Partido_inicial"]:
                    # Nuevo verso antes de encontrar final
                    break
                j += 1
            
            if not found_final:
                snippet = text[:50] + "..." if len(text) > 50 else text
                verse_problems.append((
                    verse_num,
                    snippet,
                    "Falta 'Partido_final' después de 'Partido_inicial'."
                ))
            
            # Avanzar hasta después del grupo procesado
            i = j + 1 if found_final else i + 1
            
        elif style == "Partido_medio":
            # Partido_medio sin Partido_inicial previo
            has_initial = False
            for k in range(i - 1, -1, -1):
                prev_para_idx, prev_verse_num, prev_style, prev_text = verses[k]
                if prev_style == "Partido_inicial" and prev_verse_num == verse_num:
                    has_initial = True
                    break
                elif prev_style in ["Verso"] or (prev_style == "Partido_inicial" and prev_verse_num != verse_num):
                    break
            
            if not has_initial:
                snippet = text[:50] + "..." if len(text) > 50 else text
                verse_problems.append((
                    verse_num,
                    snippet,
                    "Falta 'Partido_inicial' antes de este 'Partido_medio'."
                ))
            i += 1
            
        elif style == "Partido_final":
            # Partido_final sin Partido_inicial previo
            has_initial = False
            for k in range(i - 1, -1, -1):
                prev_para_idx, prev_verse_num, prev_style, prev_text = verses[k]
                if prev_style in ["Partido_inicial", "Partido_medio"] and prev_verse_num == verse_num:
                    has_initial = True
                    break
                elif prev_style in ["Verso"] or (prev_style in ["Partido_inicial", "Partido_final"] and prev_verse_num != verse_num):
                    break
            
            if not has_initial:
                snippet = text[:50] + "..." if len(text) > 50 else text
                verse_problems.append((
                    verse_num,
                    snippet,
                    "Falta 'Partido_inicial' o 'Partido_medio' previo."
                ))
            i += 1
            
        else:  # style == "Verso"
            i += 1
    
    # 3. Construir mensaje consolidado si hay problemas
    if verse_problems:
        count = len(verse_problems)
        plural_s = 's' if count > 1 else ''
        
        # Encabezado
        message = f"❌ ({count}) VERSO{plural_s.upper()} PARTIDO{plural_s.upper()} INCOMPLETO{plural_s.upper()}\n"
        message += "Revisa los siguientes versos:\n\n"
        
        # Listar cada verso con su problema
        for verse_num, text, problem in verse_problems:
            message += f"Verso {verse_num}. Texto: {text}\n"
            message += f"      Problema: {problem}\n\n"
        
        warnings.append(message.rstrip())
    
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
                              if v[2] in ["Verso", "Partido_inicial"]])
            
            snippet = text[:50] + "..." if len(text) > 50 else text
            warnings.append(
                f"⚠️ LAGUNA DETECTADA (después del verso {verse_num})\n"
                f"   Texto: {snippet}\n"
                f"   Revisa: ¿Es una laguna de extensión incierta o un verso específico faltante?\n"
                f"   Si es un verso específico faltante, márcalo como 'Verso' con corchetes.\n"
                f"   Total de versos actual: {total_verses}"
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
                              if v[2] in ["Verso", "Partido_inicial"]])
            
            warnings.append(
                f"⚠️ VERSO CON CORCHETES DETECTADO (verso {verse_num})\n"
                f"   Texto: {text}\n"
                f"   Revisa: ¿Es una laguna de extensión incierta?\n"
                f"   Si no sabes cuántos versos faltan, márcalo como 'Laguna' para no contarlo.\n"
                f"   Total de versos actual: {total_verses}"
            )
    
    return warnings


def validate_note_format(docx_path: str, note_type: str) -> list[str]:
    """
    Valida que todas las entradas en el archivo de notas o aparato crítico
    sigan el formato correcto:
    - NÚMERO: contenido (ej: 6: 6 cursiva y van bien centradas...)
    - @PALABRA: contenido (ej: @dedicatoria: Dedicatoria: Esta es una nota...)
    
    Devuelve una lista de warnings con las entradas que no cumplan el formato.
    """
    warnings: list[str] = []
    
    if not docx_path or not os.path.exists(docx_path):
        return warnings
    
    # Obtener el nombre del archivo para mostrarlo en el mensaje
    filename = os.path.basename(docx_path)
    
    doc = Document(docx_path)
    
    # Patrón para validar el formato correcto
    # Debe comenzar con número: o @palabra:
    pattern_verse = re.compile(r'^\d+:\s*')  # Números seguidos de :
    pattern_word = re.compile(r'^@[^@\s]+:\s*')  # @palabra seguido de :
    
    for i, para in enumerate(doc.paragraphs, 1):
        text = para.text.strip()
        
        # Ignorar párrafos vacíos o con solo espacios en blanco
        if not text:
            continue
        
        # Verificar si el párrafo cumple alguno de los formatos válidos
        is_verse_format = pattern_verse.match(text)
        is_word_format = pattern_word.match(text)
        
        if not is_verse_format and not is_word_format:
            # El párrafo no cumple ninguno de los formatos válidos
            snippet = text[:80] + "..." if len(text) > 80 else text
            warnings.append(
                f"❌ Formato incorrecto en archivo '{filename}' ({note_type}, párrafo {i}): "
                f"Debe comenzar con 'NÚMERO:' o '@PALABRA:' → Texto: {snippet}"
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
        "Titulo_comedia", "Acto", "Prosa", "Verso", "Partido_inicial",
        "Partido_medio", "Partido_final", "Personaje", "Acot",
        "Epigr_Dedic", "Epigr_Dramatis", "Dramatis_lista", "Epigr_final",
        "Laguna"  # Nuevo estilo para lagunas de extensión incierta
    }
    # Estilos que se omiten en esta validación básica porque tienen validación específica
    SKIP_STYLES = {"Cita", "Heading 1", "Heading 2", "Heading 3", "Normal"}
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
            # Validar formato de entrada (NÚMERO: o @PALABRA:)
            warnings.extend(validate_note_format(aparato_docx, "aparato crítico"))
            # Validar contenido de las notas
            aparato_notes = extract_notes_with_italics(aparato_docx)
            warnings.extend(analyze_notes(aparato_notes, "aparato"))

    # 5) Notas
    if notas_docx:
        if not os.path.exists(notas_docx):
            warnings.append(f"❌ El archivo de notas no existe: {notas_docx}")
        else:
            # Validar formato de entrada (NÚMERO: o @PALABRA:)
            warnings.extend(validate_note_format(notas_docx, "notas"))
            # Validar contenido de las notas
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


