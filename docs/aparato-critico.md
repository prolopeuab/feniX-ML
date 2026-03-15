---
layout: default
title: 2. Aparato crítico
parent: Preparación de archivos DOCX
nav_order: 2
---

# 2. Aparato crítico

Usa este archivo para registrar **solo variantes del aparato crítico**. Es independiente del texto principal y cada párrafo del DOCX corresponde a una entrada.

## Formato de entrada

### 2.1 Entradas asociadas a verso

Formato válido al inicio del párrafo:

- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:` para versos partidos)

Ejemplos:

```text
25: 25 quiero M FH : quiera ABCDEI Har Cot : querría G
329a: 329a primer tramo del verso partido ...
329b: 329b segundo tramo del verso partido ...
```

### 2.2 Entradas asociadas a término no numerado

Formato válido:

- `%palabra:`

> Para aparato por término no numerado, usa `%` (no `@`) en el archivo y en el texto principal.
{: .important }

En el archivo de aparato:

```text
%tragicomedia: tragicomedia A : tragedia Men
%dedicatoria: dedicatoria A : dedicación Men
```

> Puedes usar cursiva en el contenido del aparato (por ejemplo, siglas o testimonios). No uses etiquetas HTML (`<i>`) ni Markdown (`*...*`) en el DOCX: aplica cursiva de Word, que se transformará en `<hi rend="italic">`.
{: .tip }

En el texto principal, marca el mismo término con `%`:

```text
Título de la %tragicomedia de Lope de Vega.
```

Si la entrada afecta a una frase o unidad mayor (por ejemplo, una acotación completa), coloca la marca en el **último término** del segmento:

```text
Primera acotación con una entrada de %aparato.
```

> Usa una clave de **una sola palabra**, preferiblemente en minúsculas. El script normaliza, pero mantener una forma consistente evita confusiones.
{: .tip }

## Compatibilidad con notas explicativas

Si un mismo término necesita aparato y nota explicativa:

- En el texto principal: `@%palabra`
- En notas: `@palabra: ...`
- En aparato: `%palabra: ...`

![Ejemplo de archivo DOCX de aparato]({{ '/assets/images/capturas/preparar-docx/aparato-docx.png' | relative_url }}){: .img-100 }

## Antes de pasar al siguiente archivo

> - Usa `%palabra` (no `@palabra`) para entradas por término no numerado.
> - Mantén una entrada por párrafo y no mezcles notas y aparato en el mismo DOCX.
> - Si la entrada afecta a un segmento amplio, marca el último término del segmento en el texto principal.
> - Revisa que cada clave `%palabra` tenga su marca correspondiente y conserva cursivas cuando correspondan.
{: .tip }
