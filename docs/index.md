---
layout: default
title: Inicio
nav_order: 1
---

<p align="left">
  <img src="assets/images/logo.png" alt="Logo feniX-ML" width="200">
</p>

**feniX-ML** es una herramienta escrita en Python para convertir ediciones críticas de textos teatrales desde DOCX a XML-TEI sin necesidad de editar XML manualmente.

Está diseñada para utilizar archivos Word con estilos predefinidos y marcadores simples, con validación previa y vistas de revisión antes de exportar.

>**Compatibilidad**: Windows 10 o superior. No necesitas instalar Python si usas el ejecutable (`.exe`).

![Vista de la aplicación de escritorio]({{ '/assets/images/capturas/feniX-ML.png' | relative_url }}){: .img-50 }

## Inicio rápido

1. [Instala o descarga el ejecutable]({% link instalacion.md %}).
2. [Prepara tus DOCX con los estilos requeridos]({% link preparar-docx.md %}).
3. [Carga, valida y exporta a XML-TEI]({% link uso-app.md %}).

**Entrada/Salida:** DOCX (edición crítica) -> XML-TEI.

## Qué puedes hacer con feniX-ML

- Transformar ediciones críticas en DOCX a XML-TEI con un flujo guiado.
- Procesar el archivo principal (prólogo y texto crítico) e incorporar `Notas`, `Aparato crítico` y `Metadatos`.
- Incluir metadatos editoriales propios en el `teiHeader`.
- Validar los archivos de entrada y detectar incidencias comunes antes de convertir.
- Previsualizar el resultado en XML y en HTML local.
- Exportar un XML-TEI listo para revisión y publicación.

## Qué no esperar de feniX-ML

- No corrige automáticamente errores de marcado editorial en Word.
- No sustituye la revisión filológica ni la validación editorial final del XML.
- No ofrece edición manual del XML dentro de la interfaz.
- No permite cambiar la estructura de salida sin modificar el código fuente.


¿Te ha fallado algo? [Abrir incidencia en GitHub](https://github.com/prolopeuab/feniX-ML/issues).

## Estructura de esta guía

- [Primeros pasos e instalación]({% link instalacion.md %})
- [Preparación de archivos DOCX]({% link preparar-docx.md %})
- [Uso de la app]({% link uso-app.md %})
- [Resolución de problemas]({% link resolucion-problemas.md %})
- [Créditos]({% link creditos.md %})

## Acceso abierto

Repositorio del proyecto: [https://github.com/prolopeuab/feniX-ML](https://github.com/prolopeuab/feniX-ML)