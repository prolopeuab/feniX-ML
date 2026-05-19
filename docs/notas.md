---
layout: default
title: 3. Notas explicativas
parent: Preparación de archivos DOCX
nav_order: 3
---

# 3. Notas explicativas

Usa este archivo para registrar **solo notas explicativas**. Es independiente del texto principal y cada párrafo real del DOCX corresponde a una nota.

## Formato de entrada

### 3.1 Notas asociadas a verso

Formato válido al inicio del párrafo:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:` para versos partidos)

Ejemplos:

```text
7: Niso: rey de Megara...
329a: Primera nota para la primera parte del verso partido.
329b: Segunda nota para la parte siguiente del mismo verso.
```

### 3.2 Notas asociadas a término no numerado

Formato válido:

- `@palabra:`

> Para notas por término no numerado, usa `@` (no `%`) en el archivo y en el texto principal.
{: .important }

En el archivo de notas:

```text
@piramo: Píramo: explicación filológica del término.
@dedicatoria: dedicatoria: comentario sobre el bloque de dedicatoria.
```
> Puedes usar cursiva e hipervínculos de Word en el contenido de las notas. No uses etiquetas HTML (`<i>`) ni Markdown (`*...*`) en el DOCX: aplica cursiva de Word, que se transformará en `<hi rend="italic">`.
{: .tip }

En el texto principal, marca el mismo término con `@`:

```text
El breve poema de Tisbe y @piramo...
```

Si la nota afecta a una frase o unidad mayor (por ejemplo, una acotación completa), coloca la marca en el **último término** del segmento:

```text
Primera acotación con una entrada de @nota.
```
> Usa una clave de **una sola palabra**, preferiblemente en minúsculas. El script normaliza, pero mantener una forma consistente evita confusiones.
{: .tip }

## Compatibilidad con aparato crítico

Si un mismo término necesita nota y aparato crítico:

- En el texto principal: `@%palabra`
- En notas: `@palabra: ...`
- En aparato: `%palabra: ...`

![Archivo de notas]({{ '/assets/images/capturas/preparar-docx/notas-docx.png' | relative_url }})

## Tablas en notas

Puedes insertar una tabla simple después de una nota válida. La tabla quedará asociada a esa nota.

Si necesitas encabezado, marca la fila escribiendo `^` al principio de cada celda no vacía:

```text
^Columna 1 | ^Columna 2
Dato 1     | Dato 2
```

La primera fila no es encabezado por defecto. La marca `^` se elimina del XML final.

## Antes de pasar al siguiente archivo

> - Usa `@palabra` (no `%palabra`) para notas por término no numerado.
> - Mantén una nota por párrafo real de Word y no mezcles notas y aparato en el mismo DOCX.
> - Si la validación identifica como párrafo nuevo una línea que continúa la misma nota, hay un un salto de párrafo oculto que no se ve. Borra los espacios sobrantes o reescribe esa línea hasta que deje de saltar el aviso.
> - Si la nota afecta a un segmento amplio, marca el último término del segmento en el texto principal.
> - Revisa que cada clave `@palabra` tenga su marca correspondiente y conserva cursivas e hipervínculos cuando correspondan.
{: .tip }
