---
layout: default
title: 3. Notas explicativas
parent: Preparación de archivos DOCX
nav_order: 3
---

# 3. Notas explicativas

El archivo de notas explicativas también es independiente. Cada párrafo representa una nota.

## Formato de entrada

Formato válido al inicio de cada párrafo:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:` para versos partidos)
- `@PALABRA:` (referencia por término no numerado)

## 3.1 Notas asociadas a verso

Ejemplos:

```text
7: Niso: rey de Megara...
329a: Primera nota para la primera parte del verso partido.
329b: Segunda nota para la parte siguiente del mismo verso.
```

## 3.2 Notas asociadas a término no numerado

En el archivo de notas:

```text
@Píramo: explicación filológica del término.
@dedicatoria: comentario sobre el bloque de dedicatoria.
```

En el texto principal, marca el término con `@`:

```text
El breve poema de Tisbe y @Píramo...
```

## Si hay nota y aparato en el mismo término

Usa `@%palabra` en el texto principal y reparte contenido en ambos archivos:

- Notas: `@palabra: ...`
- Aparato: `%palabra: ...`

## Recomendaciones

- No mezcles notas y aparato en un mismo DOCX.
- Mantén una nota por párrafo.
- Revisa la secuencia de entradas repetidas para una misma clave.

![Ejemplo de archivo DOCX de notas](assets/images/capturas/preparar-docx/05-notas-docx.png)

*Captura pendiente de insertar.*
