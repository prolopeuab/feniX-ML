---
layout: default
title: Uso de la app
nav_order: 4
has_children: true
---

# Uso de la aplicación de escritorio

Una vez preparados los cuatro archivos DOCX (prólogo y texto crítico, aparato crítico, notas explicativas y metadatos), podrás generar tu edición digital en formato **XML-TEI** mediante la aplicación de escritorio **feniX-ML**.

Esta sección explica cómo usar la herramienta paso a paso:  
desde la carga de los archivos hasta la exportación final del XML, incluyendo la validación y los mensajes del programa.

---

## Flujo de trabajo

El proceso se divide en tres etapas principales:

1. **Carga de los archivos DOCX**  
   Selecciona los documentos correspondientes a cada parte de la edición.  
   feniX-ML comprueba su estructura antes de procesarlos.

2. **Validación y revisión del XML-TEI resultante**  
   El programa analiza los archivos, muestra advertencias o errores, y te indica si el contenido puede procesarse correctamente.

3. **Generar y exportar el XML-TEI**  
   Una vez validados los documentos, feniX-ML genera automáticamente el archivo final `edicion.xml`, que podrás abrir, revisar o visualizar en tu navegador.

---

## Requisitos previos

- Tener los cuatro archivos DOCX preparados según la sección [Preparar los archivos DOCX](./preparar-docx).  
- Contar con el ejecutable `feniX-ML.exe` descargado en tu equipo.  
- No es necesario tener Python instalado: la aplicación funciona de forma independiente (solo en Windows).

> Si usas macOS o Linux, tienes que ejecutar los scripts Python directamente. Consulta las instrucciones en la [sección de instalación](./instalacion).
{: .warning }

---

## Archivos que genera la aplicación

Tras ejecutar la aplicación, se crean los siguientes elementos:

- **Archivo principal XML-TEI** (`edicion.xml`): contiene la estructura completa del texto marcado.  

---

## Próximos pasos

En las páginas siguientes encontrarás las instrucciones detalladas de cada etapa:

1. [Cargar los archivos DOCX](./cargar-archivos)  
2. [Validar y revisar mensajes](./validar-y-revisar)  
3. [Generar y exportar el XML-TEI](./generar-y-exportar)

---

> Recuerda que feniX-ML añade automáticamente algunos metadatos institucionales al archivo final (autor, grupo PROLOPE y créditos de codificación).  
> 
> Si vas a reutilizar el XML en otro contexto, puedes editarlos manualmente después.
{: .important }
