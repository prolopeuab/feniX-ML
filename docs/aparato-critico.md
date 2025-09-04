---
layout: default
title: 2. Aparato crítico
parent: Preparar los archivos DOCX
nav_order: 2
---

# 2. Aparato crítico

El **aparato crítico** recoge las variantes textuales del texto y las asocia al lugar correspondiente.

Este archivo es independiente y se procesa para generar automáticamente las notas (`<note>`) de tipo aparato en el archivo XML-TEI.

---

## Formato del documento

El aparato crítico se redacta en un documento Word sencillo, siguiendo estas reglas:

- **Cada línea contiene una sola entrada del aparato crítco**.  
- Las entradas pueden ir en el orden lógico, tal y como preparas el documento para la edición *en papel*.
- A cada entrada del aparato crítico se le añade al principio el número de verso o el símbolo `@` al término afectado, si no se trata de verso. 
- No se aplican estilos de Word, que solo funcionan en el documento del texto crítico, pero sí se debe usar la cursiva cuando corresponda, que será procesada correctamente.

---

## 2.1 Entradas del aparato asociadas a un verso numerado

- Comienzan con el número del verso, seguido de `:`.
- Después, la entrada del aparato tal y como se podrá leer en la nota, siguiendo los [*Criterios de edición de PROLOPE*](https://prolope.uab.cat/wp-content/uploads/2023/12/criterios_edicion_prolope.pdf) o aquellos elegidos.
  
#### Ejemplo:

<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.05em;">
    <p>25: 25&nbsp;&nbsp;quiero <i>M</i> <i>FH</i> : quiera <i>ABCDEI</i> <i>Har</i> <i>Cot</i> : querría <i>G</i></p>
    <p>76: 76&nbsp;&nbsp;Que no son <i>Cot</i> : Que son <i>AB</i></p>
</div>

> Al procesar los archivos, feniX-ML asocia cada entrada del aparato con su verso correspondiente gracias al número + `:` agregado, y genera una <note> al final de dicho verso en el XML-TEI con el contenido de la nota.
{: .note }

---

## 2.2 Entradas del aparato asociadas a otros elementos no numerados

Cuando la variante se refiere a un elemento sin numeración de verso (por ejemplo, títulos, acotaciones, prólogo o dramatis personae), se utiliza el símbolo `@` para indicar el punto de referencia.  

Este símbolo se coloca **antes del término afectado** (o del último término del conjunto) y va seguido de `:`.  

La entrada se redacta a continuación con el mismo formato habitual, respetando las cursivas donde corresponda.

#### Ejemplo:

<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.05em;">
    <p>Dédalo@: 651<i>Acot</i>&nbsp;&nbsp;Sale Dédalo : <i>A</i> trae la acotación tras el verso 650 : <i>om</i> <i>Men</i></p>  
    <p>tragicomedia@: tragicomedia&nbsp;&nbsp;<i>A</i> : tragedia <i>Men</i></p>
</div>

> Al procesar los archivos, feniX-ML asocia cada entrada del aparato marcada con `@` al lugar del texto crítico donde se encuentra el mismo término, también marcado con `@`.
{: .note }
