---
layout: default
title: 4. Metadatos
parent: Preparación de archivos DOCX
nav_order: 4
---

# 4. Metadatos de la edición

El archivo de metadatos se usa para generar el bloque `<teiHeader>` durante la conversión.

## Requisito estructural mínimo

El DOCX de metadatos debe contener **al menos 3 tablas**:

1. Metadatos principales de la edición digital.
2. Datos bibliográficos de la fuente.
3. Lista de testimonios (`listWit`).

Si faltan tablas, la conversión lanza error.

## Campos que usa la app

### Tabla 1 (metadatos principales)

Campos esperados (según plantilla):

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

Campos esperados:

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

### Tabla 3 (testimonios)

- Primera fila: cabecera (se ignora como guía).
- Filas siguientes: sigla + descripción de testimonio.

## Tipos de TEI-header

La GUI permite elegir:

- **TEI-header PROLOPE** (`prolope`): incluye bloques institucionales y textos editoriales PROLOPE.
- **TEI-header propio** (`minimo`): mantiene estructura funcional con metadatos del usuario y referencia a la app, sin los bloques institucionales extensos.

## Si no cargas metadatos

La conversión usa una cabecera de respaldo mínima.

> Para XML final de trabajo editorial se recomienda cargar siempre el DOCX de metadatos.
{: .warning }

![Plantilla de metadatos con 3 tablas](assets/images/capturas/preparar-docx/06-metadatos-tablas.png)

*Captura pendiente de insertar.*
