---
layout: default
title: 2. Validación y vista previa
parent: Uso de la app
nav_order: 2
---

# 2. Validación y vista previa

En este paso revisas el marcado con `Validar marcado` y compruebas el resultado en `Vista previa (XML)` y `Vista previa (HTML)`. Estas funciones llaman a la misma transformación, pero la almacenan temporalmente, sin generar un archivo exportable aún.

Cuando ya existe una validación en memoria, la app muestra `Ver última` para volver a abrirla sin recalcular todo. En ese caso, el botón de validación pasa a funcionar como revalidación y muestra una flecha circular para indicar que volverá a ejecutar el proceso completo.

## Validación (`Validar marcado`)

### Qué valida

- Estilos permitidos en el archivo principal.
- Párrafos sin estilo (`Normal`) donde se espera marcado semántico.
- Secuencias de versos partidos (`Partido_inicial`, `Partido_medio`, `Partido_final`).
- Uso del estilo `Laguna`.
- Formato de entradas en `Notas` y `Aparato crítico` (`NÚMERO:`, `NÚMERO+LETRA:`, `@PALABRA:`, `%PALABRA:`).

En `Notas` y `Aparato crítico`, la validación es estricta: cada entrada debe empezar en un párrafo real de Word con uno de esos formatos. Si un aviso aparece en una línea que parecía ser continuación de la anterior, probablemente Word la guardó como párrafo independiente; únela al párrafo anterior o añade el marcador que corresponda.

### Qué no valida

- Estructura interna de la `Tabla de metadatos`.
- Validación TEI contra RelaxNG/XSD.

### Flujo recomendado

1. Pulsa `Validar marcado`.
2. Usa los filtros del modal para ocultar temporalmente tipos de aviso que ya has revisado.
3. Corrige incidencias en los DOCX de origen.
4. Pulsa `Ver última` si solo quieres consultar la validación anterior, o revalida si has hecho cambios.
5. Vuelve a validar antes de previsualizar y exportar.

Los filtros del modal permiten mostrar u ocultar categorías de avisos, por ejemplo notas múltiples por verso, notas múltiples por palabra, estilos, formato de notas, notas vacías, versos partidos, lagunas, versos con corchetes, archivos u otros mensajes. La selección de filtros se mantiene durante la sesión de la app.

### Capturas: validación

![Mensaje de validación sin errores]({{ '/assets/images/capturas/uso-app/sin-errores.png' | relative_url }})
![Mensaje de validación con errores]({{ '/assets/images/capturas/uso-app/con-errores.png' | relative_url }})
{: .img-row-2 }

## Vista previa (`XML` y `HTML`)

- `Vista previa (XML)`: abre una ventana con el XML generado en ese momento.
- `Vista previa (HTML)`: crea una vista en el navegador a partir de ese mismo XML, mediante un HTML temporal que transforma localmente con JavaScript y CSS.

En la vista HTML, las tablas solo muestran encabezado visual cuando el XML contiene filas y celdas con `role="label"`. Para producir ese encabezado desde Word, marca la fila con `^` al principio de cada celda no vacía. Las tablas sin esa marca se muestran como tablas de datos sin cabecera.

> Si detectas un problema en la vista previa, corrige el DOCX de origen y vuelve a validar. Como regla general, si el HTML se ve mal, el problema está en el XML y, por tanto, en los archivos DOCX de origen.
{: .tip }

### Captura: vista XML

![Vista previa XML]({{ '/assets/images/capturas/uso-app/vista-xml.png' | relative_url }}){: .img-100 }

### Captura: vista HTML

![Vista previa HTML]({{ '/assets/images/capturas/uso-app/vista-html.png' | relative_url }}){: .img-100 }

## Antes de exportar

> - Asegúrate de que no quedan errores de validación pendientes.
> - Revisa al menos una de las dos vistas (`XML` o `HTML`) antes de generar el archivo final.
> - Si detectas una incidencia, corrige el DOCX de origen y vuelve a validar.
{: .tip }
