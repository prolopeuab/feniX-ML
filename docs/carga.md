---
layout: default
title: 1. Carga de archivos
parent: Uso de la app
nav_order: 1
---

# 1. Carga de archivos

## Campos de la pantalla

En el bloque **Selección de archivos** aparecen cuatro entradas:

1. **Prólogo y comedia** (obligatorio)
2. **Notas** (opcional)
3. **Aparato crítico** (opcional)
4. **Tabla de metadatos** (opcional)

La selección se hace con el botón **Explora...** de cada fila.

![Selección de archivos DOCX](assets/images/capturas/uso-app/02-carga-archivos.png)

*Captura pendiente de insertar.*

## Tipo de TEI-header

Debajo de la carga de archivos aparece el selector **Tipo de TEI-header**:

- **TEI-header PROLOPE**: añade secciones institucionales y textos editoriales de PROLOPE.
- **TEI-header propio**: genera una cabecera más breve basada en los metadatos del usuario y referencia a la app.

> Este selector solo tiene efecto si has cargado la **Tabla de metadatos**.
{: .note }

![Selector de tipo de TEI-header](assets/images/capturas/uso-app/03-tipo-header.png)

*Captura pendiente de insertar.*

## Errores comunes al cargar

- **No seleccionar archivo principal**: las acciones de validar, previsualizar y exportar se bloquean.
- **Seleccionar un formato distinto de DOCX**: la conversión no se ejecuta correctamente.
- **Cargar un archivo equivocado en un campo** (por ejemplo, aparato en notas): produce avisos de formato en validación.

## Recomendación práctica

Antes de validar o exportar, verifica que cada campo contiene la ruta correcta y que el archivo principal usa los estilos de la plantilla oficial.
