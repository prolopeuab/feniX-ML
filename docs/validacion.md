---
layout: default
title: 2. Validación
parent: Uso de la app
nav_order: 2
---

# 2. Validación

La validación se ejecuta con el botón **Validar marcado**.

## Qué comprueba actualmente

La validación revisa el archivo principal y, si están cargados, también los archivos de notas y aparato.

### En el archivo principal

- Estilos permitidos en el cuerpo del texto.
- Líneas sin estilo (`Normal`) donde se espera estilo semántico.
- Secuencias de versos partidos:
  - `Partido_inicial`
  - `Partido_medio`
  - `Partido_final`
- Uso del estilo `Laguna`.
- Versos con corchetes que podrían ser lagunas.

### En notas y aparato

Formato de entrada por párrafo:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:`)
- `@PALABRA:`
- `%PALABRA:`

También detecta entradas vacías y acumulaciones múltiples para una misma clave.

## Qué no comprueba este botón

- No valida la estructura interna de la **Tabla de metadatos**.
- No valida esquema TEI contra RelaxNG/XSD.

> El archivo de metadatos se evalúa durante la conversión cuando se intenta construir el `teiHeader`.
{: .note }

## Ejemplos de mensajes habituales

- `❌ Estilo no válido: ...`
- `❌ LÍNEAS SIN ESTILO DETECTADAS (...)`
- `❌ (...) VERSOS PARTIDOS INCOMPLETOS`
- `⚠️ LAGUNA DETECTADA (...)`
- `❌ Formato incorrecto en archivo '...': Debe comenzar con 'NÚMERO:', '@PALABRA:' o '%PALABRA:'`

![Resultado de validación en cuadro de diálogo](assets/images/capturas/uso-app/04-validacion.png)

*Captura pendiente de insertar.*
