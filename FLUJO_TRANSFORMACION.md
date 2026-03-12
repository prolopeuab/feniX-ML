# Flujo real de conversión DOCX -> TEI/XML en feniX-ML

Este documento describe en profundidad el comportamiento actual de `app/tei_backend.py` tal como está implementado hoy.

## 1. Objetivo y alcance

El módulo `tei_backend.py` cubre dos capacidades principales:

1. Conversión de un DOCX principal (más opcionales de notas, aparato y metadatos) a XML-TEI.
2. Validación preventiva de consistencia documental antes de convertir.

La conversión principal se ejecuta con `convert_docx_to_tei(...)`.
La validación preventiva se ejecuta con `validate_documents(...)`.

Este documento describe el estado real actual, no un diseño ideal.

## 2. Superficie pública y contratos

## 2.1 `convert_docx_to_tei(...)`

Firma actual:

```python
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
```

Entradas:

- `main_docx`: obligatorio, con extensión `.docx`, y existente.
- `notas_docx`: opcional, si se informa debe ser `.docx` y existir.
- `aparato_docx`: opcional, si se informa debe ser `.docx` y existir.
- `metadata_docx`: opcional, si se informa debe existir.
- `tei_header`: opcional, permite inyectar cabecera TEI ya construida.
- `output_file`: opcional, ruta de salida cuando `save=True`.
- `save`: si `False`, devuelve XML en memoria.
- `header_mode`: esperado `"prolope"` o `"minimo"` para la construcción del header con metadatos.

Salidas:

- Si `save=False`: devuelve `str` con el XML completo.
- Si `save=True`: escribe en disco y devuelve `None`.

Errores frecuentes:

- `ValueError`: extensiones inválidas o marcador estrófico `$...` inválido.
- `FileNotFoundError`: falta de archivos de entrada.
- `RuntimeError`: fallos de apertura del DOCX principal o parseo de metadatos.

## 2.2 `validate_documents(...)`

Firma actual:

```python
def validate_documents(main_docx, aparato_docx=None, notas_docx=None) -> list[str]:
```

Comportamiento:

- Devuelve lista de incidencias (errores/avisos) en texto.
- No genera XML.
- Si no hay incidencias, devuelve lista vacía.

## 3. Flujo end-to-end de conversión

## 3.1 Fase de entrada y precondiciones

`convert_docx_to_tei(...)` ejecuta:

1. Validación de `main_docx` (extensión y existencia).
2. Resolución de cabecera TEI:
   - si hay `metadata_docx`, llama `parse_metadata_docx(...)`;
   - si no hay ni `metadata_docx` ni `tei_header`, usa respaldo literal `"<teiHeader>…</teiHeader>"`.
3. Apertura del principal con `Document(main_docx)`.

## 3.2 Separación `front` / `body`

La separación se apoya en `Titulo_comedia`:

- localiza hasta 2 párrafos no vacíos de ese estilo (título y posible subtítulo),
- ignora vacíos intermedios,
- termina el bloque al primer párrafo no vacío que no sea `Titulo_comedia`.

Resultado:

- `front_paragraphs = doc.paragraphs[:title_idx]`
- `body_paragraphs = doc.paragraphs[last_title_idx + 1:]`

Si no aparece ningún `Titulo_comedia`, se aborta con `RuntimeError`.

## 3.3 Preparación de notas y estado global

Antes de procesar contenido:

- carga `nota_notes` con `extract_notes_with_italics(notas_docx)` si aplica,
- carga `aparato_notes` con `extract_notes_with_italics(aparato_docx)` si aplica,
- inicializa:
  - `annotation_counter = {}`
  - `state = {"in_sp": False, "in_cast_list": False, "in_dedicatoria": False, "in_act": False}`
  - `characters = {}`
  - `act_counter = 0`
  - `verse_counter = 1`

También:

- procesa título/subtítulo con anotaciones y mayúsculas preservando etiquetas;
- extrae notas introductorias del DOCX principal con `extract_intro_footnotes(main_docx)`.

## 3.4 Construcción de `front`

Se abre:

```xml
<front xml:id="front">
  <div type="Introducción" xml:id="prologo">
    ...
  </div>
</front>
```

Luego se delega en `process_front_paragraphs_with_tables(...)`.

Este procesamiento:

- usa notas al pie de introducción (`extract_text_with_intro_notes`),
- crea cabecera principal al detectar texto que contenga `prólogo`,
- crea subsecciones por líneas con `#`,
- maneja estilos `Quote`, `Personaje`, `Verso` y párrafo normal,
- inserta tablas con `process_table_to_tei(...)` cuando la subsección activa contiene `sinopsis`.

## 3.5 Construcción de `body`

Se abre:

```xml
<body xml:id="body">
  <div type="Texto" subtype="TEXTO" xml:id="comedia">
    <head type="mainTitle" xml:id="titulo">...</head>
```

Luego recorre `body_paragraphs`:

1. omite vacíos por `is_parse_empty_paragraph(...)`,
2. detecta marcadores estróficos `$...`,
3. cierra bloques cuando cambian contextos,
4. procesa cada estilo (`Acto`, `Personaje`, `Verso`, `Partido_*`, etc.).

## 3.6 Ensamblaje final

Al terminar:

- cierra bloques pendientes con `close_current_blocks(...)`,
- cierra `</div>`, `</body>`, `</text>`, `</TEI>`,
- une con `"\n".join(...)`,
- guarda o retorna según `save`.

## 4. Mecanismos internos en profundidad

## 4.1 Pipeline de placeholders y anotaciones

Función: `extract_text_with_italics_and_annotations(...)`.

### 4.1.1 Objetivo técnico

Integrar en una misma cadena:

- texto con cursiva preservada,
- anotaciones léxicas `@`, `%`, `@%`,
- notas insertadas como XML sin romper escape de contenido.

### 4.1.2 Estructura del ciclo

Paso 1: reconstrucción de runs y marcadores de cursiva.

- Inserta `<<<ITALIC_START>>>` y `<<<ITALIC_END>>>` según transición de `run.italic`.

Paso 2: protección de marcadores antes de regex.

- Sustituye por placeholders de control:
  - `\u0001` (inicio cursiva)
  - `\u0002` (fin cursiva)

Paso 3: sustitución de anotaciones.

- Regex central: `(@%?|%)([\u0001\u0002]*)(\w+)`
- Grupos:
  - símbolo (`@`, `%`, `@%`)
  - placeholders intermedios
  - palabra destino

Para cada coincidencia:

- normaliza la palabra (sin tildes, minúscula),
- consulta notas en `nota_notes` y/o `aparato_notes`,
- consume índices secuenciales desde `annotation_counter`,
- crea `xml:id`:
  - nota: `n_<key>_<section>_<index>`
  - aparato: `a_<key>_<section>_<index>`

Paso 4: escape seguro.

- separa temporalmente bloques de nota (`<<<NOTE>>>...<<<ENDNOTE>>>`) para no escaparlos,
- escapa solo texto no estructural.

Paso 5: restauración final.

- quita delimitadores de nota,
- convierte marcadores de cursiva a `<hi rend="italic">...</hi>`.

### 4.1.3 Estructura de `annotation_counter`

Contadores independientes por tipo:

- `annotation_counter["_occurrences_nota"]`
- `annotation_counter["_occurrences_aparato"]`

Cada clave léxica mantiene su índice actual. Esto evita colisiones entre nota y aparato de la misma palabra.

### 4.1.4 Ejemplos representativos

Ejemplo 1, nota filológica:

- entrada: `Don @honor vencido`
- salida: `Don honor<note subtype="nota" ...>...</note> vencido`

Ejemplo 2, aparato:

- entrada: `%honor`
- salida: `honor<note subtype="aparato" ...>...</note>`

Ejemplo 3, anotación doble:

- entrada: `@%honor`
- salida: dos `<note>` consecutivas (nota + aparato) tras la palabra.

Ejemplo 4, cursiva mezclada:

- si símbolo/palabra está en run cursiva, la función conserva `<hi rend="italic">...</hi>` alrededor del texto visible.

## 4.2 Cadena de `who` e IDs de personajes

Este flujo es crítico para enlazar voz dramática con reparto.

### 4.2.1 Construcción de IDs de personajes

En estilo `Dramatis_lista`:

1. toma `role_name = para.text.strip()`,
2. limpia marcadores `@` para obtener `role_name_clean`,
3. genera `role_id = normalize_id(role_name_clean)`,
4. emite:

```xml
<castItem><role xml:id="role_id">...</role></castItem>
```

5. registra mapeo para resolución posterior:

```python
characters[role_name_clean] = role_id
```

### 4.2.2 Resolución de `who` en parlamentos

En estilo `Personaje`, `find_who_id(speaker, characters)` aplica:

1. coincidencia exacta insensible a mayúsculas/minúsculas,
2. coincidencia parcial:
   - speaker al inicio antes de coma,
   - speaker igual a primera palabra,
   - speaker igual a segunda palabra,
3. fuzzy matching (`difflib.get_close_matches`, `cutoff=0.6`).

Si hay match:

```xml
<sp who="#<role_id>">
```

Si no hay match:

```xml
<sp>
```

Siempre se genera `<speaker>...</speaker>` en cada `sp`.

### 4.2.3 Casos límite relevantes

- Abreviaturas (`D. JUAN`) dependen de coincidencia difusa.
- Nombres muy parecidos pueden resolverse por fuzzy al personaje incorrecto.
- Si reparto y parlamentos usan convenciones muy distintas, `who` puede quedar ausente.

## 4.3 Reglas de generación de IDs

### 4.3.1 `normalize_id(...)`

Regla aplicada:

1. elimina diacríticos,
2. reemplaza no alfanumérico por `_`,
3. pasa a minúscula.

Ejemplos típicos:

- `DOÑA ANA` -> `dona_ana`
- `DON JUAN, viejo` -> `don_juan_viejo`

### 4.3.2 IDs de notas

IDs de anotación léxica:

- `n_<clave>_<section>_<n>`
- `a_<clave>_<section>_<n>`

IDs de notas por verso numérico:

- `nota_<verso>_<n>`
- `aparato_<verso>_<n>`

IDs de versos partidos:

- `nota_<verso><sufijo>_<n>`
- `aparato_<verso><sufijo>_<n>`

## 4.4 Versos, partidos y numeración

### 4.4.1 Verso simple (`Verso`)

- dentro de `sp`: se emite `<l n="...">...</l>` e incrementa `verse_counter`.
- dentro de dedicatoria: se emite `<l>...</l>` sin `n`.

### 4.4.2 Verso partido (`Partido_inicial`, `Partido_medio`, `Partido_final`)

`Partido_inicial`:

- crea sufijo `a`,
- emite `<l part="I" n="Na">`,
- incrementa `verse_counter`.

`Partido_medio`:

- reutiliza número base del verso actual,
- sufijo `b`, `c`, etc.,
- emite `<l part="M" n="Nb">`.

`Partido_final`:

- cierra secuencia con sufijo correspondiente,
- emite `<l part="F" n="Nc">`,
- limpia estado de verso partido.

### 4.4.3 Relación con notas

- En `Partido_inicial` hay fallback a clave base numérica si no existe clave con sufijo.
- En `Partido_medio` y `Partido_final` se usan claves con sufijo sin fallback numérico base.

## 4.5 Header de metadatos

Función: `parse_metadata_docx(...)`.

Resumen operativo:

- exige al menos 3 tablas;
- `main_meta` desde tabla 1;
- `source_meta` desde tabla 2;
- `witnesses` desde tabla 3 (saltando cabecera).

Diferencia de modos:

- `prolope`: añade componentes institucionales extra;
- `minimo`: simplifica varios bloques textuales.

Salida:

- string XML de `<teiHeader>...</teiHeader>`.

## 4.6 Front y tablas

### 4.6.1 `process_front_paragraphs_with_tables(...)`

Mecánica relevante:

- bufferiza párrafos para vaciar con contexto (`flush_paragraph_buffer`),
- gestiona estado `in_sp_front`,
- inserta tablas solo al detectar subsección `sinopsis`.

### 4.6.2 `process_table_to_tei(...)`

Estrategia:

- genera `<table rend="rules">`,
- fila de cabecera,
- fila vacía separadora,
- filas de datos con reglas especiales para:
  - fila de celda única (`cols="ncols"`),
  - filas resumen (`total`, `resumen`).

## 5. Mapa de estilos DOCX -> TEI emitido

| Entrada | Salida | Condición/nota |
|---|---|---|
| `$tipo` | `<milestone unit="stanza" type="..."/>` | Solo en `sp` o dedicatoria. |
| `Epigr_Dedic` | `<div type="dedicatoria"...>` + `<head ...>` | Primer head `mainTitle`, siguientes `subTitle`. |
| `Epigr_Dramatis` | `<div type="castList"...><head...><castList>` | Abre bloque de reparto. |
| `Dramatis_lista` | `<castItem><role xml:id="...">...</role></castItem>` | Actualiza `characters`. |
| `Acto` | `<div type="subsection" subtype="ACTO"...>` | Cierra bloques previos. |
| `Personaje` | `<sp who="#...">` o `<sp>` + `<speaker>` | Depende de `find_who_id`. |
| `Verso` | `<l n="...">` o `<l>` | Numerado solo en `sp`. |
| `Partido_inicial` | `<l part="I" n="...a">` | Crea y avanza secuencia. |
| `Partido_medio` | `<l part="M" n="...b">` | Conserva base de verso. |
| `Partido_final` | `<l part="F" n="...c">` | Cierra secuencia. |
| `Laguna` | `<gap>` | Solo en `sp` o dedicatoria. |
| `Acot` | `<stage>` | Dentro de `sp` o suelta según estado. |
| `Prosa` | `<p>` | Se procesa en primera rama `Prosa`. |
| `Epigr_final` | `<trailer>` | Si hay contenido no vacío. |

## 6. Microanálisis por función crítica

## 6.1 `extract_intro_footnotes(...)`

Objetivo:

- leer notas al pie desde `word/footnotes.xml`.

Entrada:

- ruta DOCX principal.

Salida:

- dict `{id_nota: contenido_con_hi}`.

Decisiones internas:

- parsea runs de cada nota,
- conserva cursiva,
- escapa caracteres XML.

## 6.2 `extract_notes_with_italics(...)`

Objetivo:

- convertir DOCX de notas/aparato en diccionario normalizado.

Entrada:

- ruta a DOCX de notas.

Salida:

- dict con claves `int` (verso) o `str` (léxicas/sufijos), siempre con valores `list[str]`.

Decisiones internas:

- verso con sufijo (`329a`) se queda como `str`,
- verso sin sufijo (`329`) se convierte a `int`,
- claves léxicas se normalizan a minúscula sin tildes.

## 6.3 `find_who_id(...)`

Objetivo:

- resolver `role_id` de parlamento en función del speaker.

Entrada:

- speaker textual del párrafo,
- diccionario `characters`.

Salida:

- `role_id` o `""`.

Decisiones internas:

- exacto -> parcial -> fuzzy.

## 6.4 `count_verses_in_document(...)`

Objetivo:

- reproducir la lógica de numeración del procesamiento principal.

Salida:

- lista de tuplas `(para_idx, verse_number, style, text)`.

Uso:

- base para validaciones de versos partidos, lagunas y contexto.

## 6.5 `validate_documents(...)` y auxiliares

Objetivo:

- detectar problemas antes de convertir.

Subvalidaciones clave:

- formato de notas (`validate_note_format`),
- análisis de multiplicidad/vacíos (`analyze_notes`),
- estilos no válidos y líneas sin estilo (`analyze_main_text`),
- coherencia de versos partidos (`validate_split_verses`, `validate_split_verses_impact_on_numbering`),
- validaciones de laguna/corchetes (`validate_Laguna`, `validate_verso_con_corchetes`).

## 7. Incidencias y mejoras (por severidad)

## 7.1 Alta severidad

1. **Uso de `hasattr(state, "pending_split_verse")` sobre `dict`**.
   Impacto: la lógica de seguimiento de verso partido puede no ejecutarse como se espera en ramas `Partido_*` y en aviso final.

2. **Dependencia rígida de `word/footnotes.xml`** en `extract_intro_footnotes(...)`.
   Impacto: si ese recurso no existe, la conversión puede abortar.

3. **Escape incompleto en `parse_metadata_docx(...)`**.
   Impacto: metadatos con caracteres XML especiales pueden romper el XML de salida.

4. **Versos fuera de `sp` o dedicatoria no se emiten**.
   Impacto: pérdida silenciosa de contenido en ciertos documentos mal estilados.

## 7.2 Severidad media

1. **Doble rama `elif style == "Prosa"` en `convert_docx_to_tei(...)`**.
   Impacto: una de las ramas queda inalcanzable; reduce claridad y puede ocultar intención de diseño.

2. **Marcadores `$...` fuera de contexto se descartan**.
   Impacto: posible pérdida silenciosa de hitos estróficos.

3. **Asimetría de fallback de notas en versos partidos**.
   Impacto: `Partido_inicial` y `Partido_medio/final` no aplican la misma estrategia de recuperación.

4. **Regex de anotación basada en `\w+`**.
   Impacto: palabras con guion u otros separadores no se anotan.

5. **`find_who_id(...)` puede resolver ambiguamente por fuzzy**.
   Impacto: asignación potencialmente incorrecta de `who` en el XML.

6. **`header_mode` no valida explícitamente valores fuera de `"prolope"`/`"minimo"`**.
   Impacto: comportamiento implícito no documentado si llega un valor inesperado.

## 7.3 Severidad baja

1. **Funciones no usadas en flujo principal** (`process_annotations_raw`, `process_annotations_with_ids`).
   Impacto: deuda de mantenimiento/documentación.

2. **`process_table_to_tei(...)` usa solo `paragraphs[0]` en cada celda**.
   Impacto: contenido adicional de la celda puede no serializarse.

3. **Reglas de estilo front/body dependen de nomenclatura exacta**.
   Impacto: sensibilidad alta a variaciones editoriales del DOCX.

4. **Cabecera de respaldo mínima** (`"<teiHeader>…</teiHeader>"`).
   Impacto: salida válida estructuralmente, pero con metadatos insuficientes para ciertos usos.

## 8. Verificación documental aplicada a este archivo

Este documento cubre:

- flujo general de conversión,
- contratos de APIs públicas,
- microanálisis de funciones críticas,
- pipeline profundo de placeholders,
- cadena completa de generación de `who` e IDs,
- incidencias ampliadas por severidad con impacto.

No incluye comparativas históricas ni referencias a versiones previas.

## 9. Referencia de funciones documentadas

- `convert_docx_to_tei(...)`
- `validate_documents(...)`
- `extract_text_with_italics_and_annotations(...)`
- `find_who_id(...)`
- `normalize_id(...)`
- `parse_metadata_docx(...)`
- `process_front_paragraphs_with_tables(...)`
- `process_table_to_tei(...)`
- `extract_notes_with_italics(...)`
- `count_verses_in_document(...)`
- `validate_split_verses(...)`
- `validate_split_verses_impact_on_numbering(...)`
- `validate_Laguna(...)`
- `validate_verso_con_corchetes(...)`

Este archivo debe leerse como una especificación operativa profunda del estado actual de `tei_backend.py`.
