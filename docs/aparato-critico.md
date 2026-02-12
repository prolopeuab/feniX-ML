---
layout: default
title: 2. Aparato crítico
parent: Preparación de archivos DOCX
nav_order: 2
---

# 2. Aparato crítico

El archivo de aparato crítico es independiente del texto principal. Cada párrafo del DOCX contiene una entrada.

## Formato de entrada

Formato válido al inicio de cada párrafo:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:` para versos partidos)
- `%PALABRA:` (referencia por término no numerado)

> Para aparato crítico por término no numerado, usa `%` (no `@`) en archivo y texto principal.
{: .important }

## 2.1 Entradas asociadas a verso

Ejemplos:

```text
25: 25 quiero M FH : quiera ABCDEI Har Cot : querría G
329a: 329a primer tramo del verso partido ...
329b: 329b segundo tramo del verso partido ...
```

## 2.2 Entradas asociadas a término no numerado

En el archivo de aparato:

```text
%tragicomedia: tragicomedia A : tragedia Men
%dedicatoria: dedicatoria A : dedicación Men
```

En el texto principal, marca el mismo término con `%`:

```text
Título de la %tragicomedia de Lope de Vega.
```

## Compatibilidad con notas explicativas

Si un mismo término necesita aparato y nota explicativa:

- En el texto principal: `@%palabra`
- En notas: `@palabra: ...`
- En aparato: `%palabra: ...`

## Recomendaciones

- Mantén una entrada por párrafo.
- Conserva cursivas cuando correspondan (se preservan en salida).
- Evita mezclar aparato y notas en un mismo archivo.

![Ejemplo de archivo DOCX de aparato](assets/images/capturas/preparar-docx/04-aparato-docx.png)

*Captura pendiente de insertar.*
