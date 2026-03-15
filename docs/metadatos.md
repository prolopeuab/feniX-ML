---
layout: default
title: 4. Metadatos
parent: Preparación de archivos DOCX
nav_order: 4
---

# 4. Metadatos de la edición

El archivo de metadatos se usa para generar el bloque `<teiHeader>` durante la conversión.

## Checklist rápido

1. El DOCX contiene **3 tablas** en este orden: metadatos principales, fuente bibliográfica y testimonios.
2. La **primera fila** de la tabla de testimonios es cabecera (la app la ignora).
3. Cada fila representa una única entrada (clave + valor).

> Si faltan tablas (menos de 3), la conversión falla.
{: .important }

## Estructura mínima obligatoria

El único requisito estrictamente obligatorio es la estructura de 3 tablas.

Aunque algunos campos pueden quedar vacíos, se recomienda completarlos para evitar un `teiHeader` incompleto.

## Campos que reconoce la app (coincidencia exacta)

Usa los nombres de campo tal como aparecen en la plantilla. Si cambias etiquetas, la app puede dejar datos sin mapear.

### Tabla 1 (metadatos principales)

Campos reconocidos:

- `Título comedia`
- `Autor`
- `Editor`
- `Responsable/s revisión`
- `Responsable marcado automático`
- `Versión`
- `Publicado por`
- `Lugar publicación`
- `Fecha publicación`

### Tabla 2 (fuente bibliográfica)

Campos reconocidos:

- `Título comedia`
- `Subtítulo`
- `Título volumen`
- `Parte`
- `Coordinadores volumen`
- `Publicado por`
- `Lugar publicación`
- `Fecha publicación`
- `Volumen`
- `Páginas`

### Tabla 3 (testimonios / `listWit`)

- `sigla` + descripción del testimonio.

> La sigla se usa como `xml:id`. Recomendación: sin espacios, sin símbolos raros y mejor comenzar por letra.
{: .tip }

## Tipos de TEI-header

La GUI permite elegir:

- **TEI-header PROLOPE** (`prolope`): incluye datos propios del proyecto.
- **TEI-header propio** (`minimo`): mantiene estructura funcional con metadatos del usuario y referencia a la app.

## Si no cargas metadatos

La conversión usa una cabecera de respaldo mínima.

> Se recomienda cargar siempre el DOCX de metadatos para evitar correcciones manuales posteriores en el XML.
{: .tip }

![Archivo de metadatos]({{ '/assets/images/capturas/preparar-docx/metadatos-docx.png' | relative_url }})

## Antes de continuar

> - Comprueba que el DOCX mantiene las 3 tablas en el orden correcto.
> - Verifica que los nombres de campo coinciden exactamente con la plantilla.
> - En `Carga de archivos`, sube este DOCX en `Tabla de metadatos` y revisa `Tipo de TEI-header`.
{: .tip }
