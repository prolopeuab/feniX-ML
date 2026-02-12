---
layout: default
title: 3. Exportación
parent: Uso de la app
nav_order: 3
---

# 3. Exportación y vista previa

## Vista previa antes de exportar

La app ofrece dos vistas previas:

1. **Vista previa (XML)**
   - Abre una ventana interna con el XML generado.
   - Útil para revisar estructura y etiquetas.

2. **Vista previa (HTML)**
   - Genera un HTML temporal y lo abre en el navegador.
   - Renderiza TEI con CETEIcean y estilos de `app/resources/estilos.css`.

![Vista previa XML](assets/images/capturas/uso-app/05-vista-previa-xml.png)

*Captura pendiente de insertar.*

![Vista previa HTML](assets/images/capturas/uso-app/06-vista-previa-html.png)

*Captura pendiente de insertar.*

## Guardado final

Para exportar el XML:

1. (Opcional) Define ruta y nombre en **Archivo**.
2. Pulsa **Generar archivo XML-TEI**.

Comportamiento de nombre/ruta:

- Si defines ruta manual, la app guarda ahí el `.xml`.
- Si no defines ruta, la app genera nombre automáticamente a partir del título y guarda en el directorio de ejecución.

## Checklist rápido antes de exportar

- Archivo principal seleccionado.
- Validación ejecutada y revisada.
- Marcadores `@`, `%` y `@%` revisados en texto principal.
- Formato de notas/aparato revisado (`NÚMERO:`, `NÚMERO+LETRA:`, `@PALABRA:`, `%PALABRA:`).
- Metadatos cargados si necesitas un `teiHeader` completo.
