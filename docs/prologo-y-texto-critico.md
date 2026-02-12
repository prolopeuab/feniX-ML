---
layout: default
title: 1. Prólogo y texto crítico
parent: Preparación de archivos DOCX
nav_order: 1
---

# 1. Prólogo y texto crítico

Este archivo DOCX reúne dos bloques en un solo documento:

1. **Prólogo o estudio introductorio**
2. **Texto crítico de la comedia**

La app convierte este archivo según estilos de Word y marcadores textuales. Para evitar errores, trabaja siempre sobre la plantilla del proyecto.

## Estructura general del documento

Orden recomendado:

1. Prólogo (con secciones `#...`)
2. Título de la comedia (`Titulo_comedia`)
3. Resto del texto crítico (dedicatoria, dramatis personae, actos, intervenciones, etc.)

![Estructura general del DOCX principal](assets/images/capturas/preparar-docx/01-estructura-prologo-comedia.png)

*Captura pendiente de insertar.*

## 1.1 El prólogo

### Secciones con `#`

Las secciones del prólogo se marcan con líneas que empiezan por `#` (sin espacio obligatorio después):

```text
#Prólogo
Texto...

#Estudio
Texto...
```

Estas líneas se interpretan como encabezados de subsección en el bloque `<front>`.

### Citas en el prólogo

Para citas extensas usa el estilo de Word **`Quote`**. Se transforma en bloque de cita TEI.

### Notas del prólogo

Las notas del prólogo se insertan como **notas al pie de Word**. La app las transforma en notas TEI de tipo introductorio.

### Tabla de sinopsis

La sección de sinopsis puede incluir tabla. La app procesa tablas en el front (especialmente en la sección de sinopsis).

## 1.2 El texto crítico

Desde el primer `Titulo_comedia`, la app procesa el cuerpo principal (`<body>`).

### Estilos reconocidos y salida TEI

| Estilo en Word | Uso | Salida TEI principal |
|---|---|---|
| `Titulo_comedia` | Título (y posible subtítulo si hay segunda línea consecutiva) | `<head type="mainTitle">` y opcional `<head type="subTitle">` |
| `Epigr_Dedic` | Epígrafe de dedicatoria | `<div type="dedicatoria">` + `<head ...>` |
| `Epigr_Dramatis` | Encabezado de dramatis personae | `<div type="castList">` + `<head type="castListTitle">` |
| `Dramatis_lista` | Entrada de personaje en lista | `<castItem><role ...>` |
| `Acto` | Encabezado de acto | `<div type="subsection" subtype="ACTO">` |
| `Personaje` | Inicio de intervención | `<sp>` + `<speaker>` |
| `Verso` | Verso completo | `<l n="...">` |
| `Partido_inicial` | Primer tramo de verso partido | `<l part="I" n="123a">` |
| `Partido_medio` | Tramo intermedio | `<l part="M" n="123b">` |
| `Partido_final` | Tramo final | `<l part="F" n="123c">` |
| `Acot` | Acotación escénica | `<stage>` |
| `Prosa` | Párrafo en prosa | `<p>` |
| `Laguna` | Laguna de extensión incierta | `<gap>` |
| `Epigr_final` | Cierre/epígrafe final | `<trailer>` |

> `Laguna` no incrementa la numeración de versos.
{: .note }

![Aplicación de estilos en Word](assets/images/capturas/preparar-docx/02-estilos-word.png)

*Captura pendiente de insertar.*

## Símbolos y marcadores en el texto principal

Además de estilos, feniX-ML usa marcadores inline.

### Anotaciones por palabra

- `@palabra` -> nota explicativa (archivo de notas).
- `%palabra` -> aparato crítico (archivo de aparato).
- `@%palabra` -> ambas notas sobre el mismo término.

Ejemplo:

```text
Salen @Teseo y %Albante en silencio.
```

### Cambio de forma estrófica

Para indicar inicio de nueva forma estrófica, usa una línea que empiece por `$`:

```text
$redondilla
$endecasílabos sueltos
```

Se convierte en:

```xml
<milestone unit="stanza" type="redondilla"/>
<milestone unit="stanza" type="endecasilabos-sueltos"/>
```

![Marcadores @ % @% y $](assets/images/capturas/preparar-docx/03-marcadores-anotaciones.png)

*Captura pendiente de insertar.*

## Notas y aparato por verso

Para versos numerados, las notas y variantes se vinculan por número de verso en archivos separados (`notas.docx` y `aparato.docx`), usando formatos como:

- `25:`
- `329a:` (verso partido, parte con sufijo)

## Casos particulares

### Dedicatoria

En dedicatoria usa `Epigr_Dedic` para encabezado y aplica estilo `Prosa` o `Verso` según corresponda en el contenido. No se recomienda dejar texto de dedicatoria en `Normal`.

### Verso interrumpido por acotación

Si un personaje continúa tras una acotación, repite `Personaje` para abrir una nueva intervención de forma explícita.

### Errores que conviene evitar

- Estilos con nombre mal escrito (ej. `Partido_incial`).
- Párrafos en `Normal` dentro del cuerpo.
- Secuencias de verso partido sin cierre (`Partido_final`).
