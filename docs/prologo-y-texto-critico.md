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

1. Prólogo (con secciones `#...`)
2. Título de la comedia (`Titulo_comedia`)
3. Resto del texto crítico (dedicatoria, dramatis personae, actos, intervenciones, etc.)

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

### Citas y versos en el prólogo
Además de párrafos de texto, el prólogo puede incluir elementos especiales como citas textuales de otros textos o de la propia obra editada. En el primer caso, usa el estilo cita (`quote`), en el segundo, puedes usar los estilos para personajes, versos, versos partidos y acotaciones con normalidad, como harías en el texto crítico (descrito más abajo).

En el prólogo, tanto `Verso` como `Partido_inicial` / `Partido_medio` / `Partido_final` se convierten en `<l>`, pero sin numeración `@n`. La numeración de versos partidos con sufijos (`123a`, `123b`, `123c`) se mantiene solo en el cuerpo de la obra.

### Notas del prólogo

Las notas del prólogo se insertan como notas al pie de Word. La app las transforma en notas TEI de tipo introductorio (`<note type="intro"`).

### Tabla de sinopsis

La sección de sinopsis puede incluir tabla. La app procesa tablas en el front (especialmente en la sección de sinopsis).

![El prólogo en el documento Word]({{ '/assets/images/capturas/preparar-docx/prologo-docx.png' | relative_url }}){: .img-100 }

## 1.2 El texto crítico

Desde el primer `Titulo_comedia`, la app procesa el cuerpo principal (`<body>`).

![El inicio del texto crítico]({{ '/assets/images/capturas/preparar-docx/comedia-docx.png' | relative_url }}){: .img-100 }

### Estilos reconocidos y salida TEI

| Estilo en Word | Uso | Salida TEI principal |
|---|---|---|
| `Titulo_comedia` | Título (y posible subtítulo si hay segunda línea consecutiva) | `<head type="mainTitle">` y opcional `<head type="subTitle">`; si se repite pegado a un `Acto`, se interpreta como título repetido de ese acto |
| `Epigr_Dedic` | Epígrafe de dedicatoria | `<div type="dedicatoria">` + `<head ...>` |
| `Epigr_Dramatis` | Encabezado de dramatis personae | `<div type="castList">` + `<head type="castListTitle">`; si aparece dentro de un acto abierto, se asocia a ese acto |
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

![Aplicación de estilos en Word]({{ '/assets/images/capturas/preparar-docx/estilos-docx.png' | relative_url }}){: .img-50 }

Si una obra repite el título de la comedia al comienzo de cada acto, puedes reutilizar `Titulo_comedia` sin crear estilos nuevos. La app lo interpretará como título repetido del acto cuando aparezca inmediatamente antes o después de `Acto`. Si además el dramatis del acto va entre ese título repetido y el `Acto`, también se asociará al mismo acto.

Del mismo modo, puedes reutilizar `Epigr_Dramatis` y `Dramatis_lista` dentro de un acto para codificar un dramatis personae específico de ese acto. También pueden aparecer inmediatamente antes de `Acto`, después de un `Titulo_comedia` repetido, y se asociarán al acto siguiente. Fuera de esos contextos, esos mismos estilos siguen funcionando como dramatis global de la obra.

### Estructuras válidas del cuerpo

El caso más habitual es este:

```text
Titulo_comedia
Epigr_Dramatis
Dramatis_lista
Acto
...
Acto
...
```

Pero también es válido este otro, sin dramatis general y con bloque propio en cada acto:

```text
Titulo_comedia

Titulo_comedia
Epigr_Dramatis
Dramatis_lista
Acto
...

Titulo_comedia
Epigr_Dramatis
Dramatis_lista
Acto
...
```

En ese segundo patrón, la app interpreta cada secuencia `Titulo_comedia` + `Epigr_Dramatis` + `Dramatis_lista` + `Acto` como el arranque de un acto. En TEI:

- el `Titulo_comedia` repetido se convierte en `<head type="mainTitle" subtype="repeated">` y, si hay una segunda línea consecutiva, en `<head type="subTitle" subtype="repeated">`
- el dramatis de ese bloque se anida dentro del acto como `castList`
- los personajes definidos ahí tienen prioridad dentro de ese acto frente a un dramatis global, si también existe

## Marcadores que debes usar en este archivo

Además de estilos de Word, feniX-ML usa marcadores inline en el **texto principal**.

### 1) Marcadores de nota y aparato (`@`, `%`, `@%`)

- `@palabra` -> marca un término con nota explicativa.
- `%palabra` -> marca un término con aparato crítico.
- `@%palabra` -> marca un término con nota y aparato a la vez.

> Usa `@`, `%` y `@%` solo en elementos no numerados (títulos, dedicatoria, acotaciones, etc.).
> En versos numerados no hace falta usar estos símbolos: notas y aparato se vinculan por número de verso en sus archivos correspondientes.
{: .important }

Ejemplo:

```text
Salen @Teseo y %Albante en silencio.
```

Para el formato completo de notas y aparato, consulta:

- [2. Aparato crítico]({% link aparato-critico.md %})
- [3. Notas explicativas]({% link notas.md %})

### 2) Marcadores de cambio estrófico (`$`)

Usa una línea que empiece por `$` para marcar un cambio de forma métrica.

```text
$redondilla
$endecasílabos sueltos
```

> Puedes usar `$` en cada cambio de segmento métrico o en cada estrofa, según el nivel de detalle que necesites.
{: .tip }

### Versos partidos

Para versos partidos, usa la secuencia de estilos `Partido_inicial` -> `Partido_medio` -> `Partido_final`.

En el cuerpo de la obra, estos estilos se convierten en `<l part="I|M|F" n="...">`. En el prólogo se usan los mismos estilos, pero la salida conserva `part="I|M|F"` sin añadir `@n`.

![Ejemplo de versos partidos]({{ '/assets/images/capturas/preparar-docx/partidos-docx.png' | relative_url }}){: .img-70 }


## Casos particulares

### Dedicatoria

En dedicatoria usa `Epigr_Dedic` para encabezado y aplica estilo `Prosa`, `Verso` o `Partido_*` según corresponda en el contenido. No dejar texto `Normal` (sin estilo).

### Verso interrumpido por acotación

Si un personaje continúa tras una acotación, no es necesario reabrir `Personaje` de forma explícita, el sistema incluirá el `<stage>` dentro de ese `<sp>`.

### Versos omitidos o lagunas textuales
Cuando hay pérdida de texto, elige el estilo según cómo quieras tratar la numeración:

- Usa `Verso` si conoces los versos omitidos y quieres mantener su numeración en la secuencia.
- Usa `Laguna` si no conoces cuántos versos faltan o no quieres que computen en la numeración.

![Versos omitidos o lagunas textuales]({{ '/assets/images/capturas/preparar-docx/laguna-docx.png' | relative_url }}){: .img-50 }

## Antes de pasar al siguiente archivo

> - Revisa que no queden estilos mal escritos (por ejemplo, `Partido_incial`).
> - Comprueba que no haya párrafos en `Normal` dentro del cuerpo.
> - Verifica que toda secuencia de verso partido cierre con `Partido_final`.
{: .tip }
