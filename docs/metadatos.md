---
layout: default
title: 4. Metadatos
parent: Preparar los archivos DOCX
nav_order: 4
---

# 4. Metadatos de la edición

El archivo de **metadatos** contiene la información descriptiva de la edición y de sus fuentes.  
feniX-ML utiliza este archivo para generar automáticamente el bloque `<teiHeader>` del XML-TEI.

---

## Formato del documento

- Se debe completar el documento Word con **las tablas incluidas en la [plantilla](https://github.com/prolopeuab/feniX-ML/ejemplos)**:  
  - **Metadatos principales**: datos de la edición crítica digital que se está generando.  
  - **Datos bibliográficos de la fuente**: información sobre la edición base.  
  - **Siglas de los testimonios** utilizados para la edición crítica.

- No es necesario aplicar estilos. 
- No se debe modificar el formato de la tabla.


#### Ejemplo de estructura

<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.05em;">
<table>
<tr><td><b>Título comedia</b></td><td>El laberinto de Creta</td></tr>
<tr><td><b>Autor</b></td><td>Félix Lope de Vega Carpio</td></tr>
<tr><td><b>Editor</b></td><td>Sònia Boadas</td></tr>
<tr><td><b>Publicado por</b></td><td>PROLOPE, Universitat Autònoma de Barcelona</td></tr>
<tr><td><b>Fecha publicación</b></td><td>2025</td></tr>
</table>
</div>

---

### ℹ️ Metadatos añadidos automáticamente por feniX-ML

Además de los datos completados en el archivo de metadatos, feniX-ML incorpora automáticamente información fija en el `<teiHeader>`:

- **Autor**: siempre se añade “Félix Lope de Vega Carpio” como autor de la obra.  
- **Referencia institucional**: se incluyen referencias al Grupo PROLOPE, a la Biblioteca Digital PROLOPE y al responsable de dirección.  
- **Crédito de codificación**: se añade un párrafo indicando que el marcado ha sido realizado con la aplicación feniX-ML.

> Si el archivo se utiliza para ediciones que no pertenecen a PROLOPE, estos datos deberán modificarse manualmente en el XML generado o modificar previamente el script.

---

## Consejos finales

- Completa **todas las casillas** de la tabla para evitar errores de validación.  
- Respeta el formato de la plantilla: no cambies el diseño de las tablas.  
- Puedes incluir tantos testimonios como sea necesario en la última sección.

---
