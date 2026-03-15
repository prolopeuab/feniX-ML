---
layout: default
title: 2. Validación y vista previa
parent: Uso de la app
nav_order: 2
---

# 2. Validación y vista previa

En este paso revisas el marcado con `Validar marcado` y compruebas el resultado en `Vista previa (XML)` y `Vista previa (HTML)`. Estas funciones llaman a la misma transformación, pero la almacenan temporalmente, sin generar un archivo exportable aún.

## Validación (`Validar marcado`)

### Qué valida

- Estilos permitidos en el archivo principal.
- Párrafos sin estilo (`Normal`) donde se espera marcado semántico.
- Secuencias de versos partidos (`Partido_inicial`, `Partido_medio`, `Partido_final`).
- Uso del estilo `Laguna`.
- Formato de entradas en `Notas` y `Aparato crítico` (`NÚMERO:`, `NÚMERO+LETRA:`, `@PALABRA:`, `%PALABRA:`).

### Qué no valida

- Estructura interna de la `Tabla de metadatos`.
- Validación TEI contra RelaxNG/XSD.

### Flujo recomendado

1. Pulsa `Validar marcado`.
2. Corrige incidencias en los DOCX de origen.
3. Vuelve a validar antes de previsualizar y exportar.

### Capturas: validación

![Mensaje de validación sin errores]({{ '/assets/images/capturas/uso-app/sin-errores.png' | relative_url }})
![Mensaje de validación con errores]({{ '/assets/images/capturas/uso-app/con-errores.png' | relative_url }})
{: .img-row-2 }

## Vista previa (`XML` y `HTML`)

- `Vista previa (XML)`: abre una ventana con el XML generado en ese momento.
- `Vista previa (HTML)`: crea una vista en el navegador a partir de ese mismo XML, mediante un HTML temporal que transforma localmente con JavaScript y CSS.

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
