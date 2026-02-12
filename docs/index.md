---
layout: default
title: Inicio
nav_order: 1
---

<p align="left">
  <img src="assets/images/logo.png" alt="Logo feniX-ML" width="200">
</p>

**feniX-ML** es una herramienta para convertir ediciones críticas teatrales desde DOCX a XML-TEI sin necesidad de editar XML manualmente.

Está orientada a un flujo editorial en Word basado en estilos y marcadores simples, con validación previa y vistas de revisión antes de exportar.

## Qué puedes hacer con feniX-ML

- Cargar el archivo principal (`Prólogo y comedia`) y, opcionalmente, `Notas`, `Aparato crítico` y `Metadatos`.
- Seleccionar tipo de cabecera: `TEI-header PROLOPE` o `TEI-header propio`.
- Validar marcado y detectar incidencias comunes antes de convertir.
- Previsualizar el resultado en XML y HTML.
- Generar el XML-TEI final.

## Convenciones de marcado clave

En el texto principal:

- `@palabra` -> nota explicativa.
- `%palabra` -> aparato crítico.
- `@%palabra` -> ambos tipos.
- `$tipo de estrofa` -> marcador estrófico (`milestone`).

En archivos de notas/aparato:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:`)
- `@PALABRA:`
- `%PALABRA:`

## Estructura de esta guía

- [Primeros pasos e instalación](./instalacion)
- [Preparación de archivos DOCX](./preparar-docx)
- [Uso de la app](./uso-app)
- [Resolución de problemas](./resolucion-problemas)
- [Créditos](./creditos)

## Acceso abierto

Repositorio del proyecto: [https://github.com/prolopeuab/feniX-ML](https://github.com/prolopeuab/feniX-ML)
