---
layout: default
title: Uso de la app
nav_order: 4
has_children: true
---

# Uso de la aplicación de escritorio

Esta sección describe el flujo real de trabajo en la interfaz de feniX-ML, tal como funciona actualmente.

## Flujo general

1. Cargar el archivo **Prólogo y comedia** (obligatorio).
2. Cargar opcionalmente **Notas**, **Aparato crítico** y **Tabla de metadatos**.
3. Elegir el tipo de encabezado en **Tipo de TEI-header**:
   - `TEI-header PROLOPE`
   - `TEI-header propio`
4. Ejecutar **Validar marcado** para revisar incidencias.
5. Revisar resultado con **Vista previa (XML)** y/o **Vista previa (HTML)**.
6. Guardar el resultado con **Generar archivo XML-TEI**.

![Pantalla principal de feniX-ML](assets/images/capturas/uso-app/01-pantalla-principal.png)

*Captura pendiente de insertar.*

## Qué archivos son obligatorios

- Obligatorio: `Prólogo y comedia`.
- Opcionales: `Notas`, `Aparato crítico`, `Tabla de metadatos`.

> Si no cargas metadatos, la app genera un `teiHeader` de respaldo mínimo. Para una edición final, se recomienda siempre aportar el archivo de metadatos.
{: .warning }

## Subpáginas de esta sección

1. [1. Carga de archivos](./carga)
2. [2. Validación](./validacion)
3. [3. Exportación y vista previa](./exportacion)

## Notas de uso importantes

- La app trabaja con DOCX y estilos de Word de la plantilla del proyecto.
- El nombre final del XML no es fijo (no se genera siempre como `edicion.xml`).
- Puedes abrir ayuda desde el menú **Ayuda** de la aplicación para acceder a documentación y plantillas.
