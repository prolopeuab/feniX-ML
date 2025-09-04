---
layout: default
title: 3. Notas explicativas
parent: Preparar los archivos DOCX
nav_order: 3
---

# 3. Notas explicativas

Las **notas explicativas** recogen comentarios filológicos, históricos o culturales que acompañan al texto crítico.  

Este archivo es independiente y se procesa para generar automáticamente las notas (`<note>`) de tipo explicativa en el archivo XML-TEI.

---

## Formato del documento

- **Cada párrafo contiene una sola nota.**  
- Si la nota se refiere a un verso, comienza con su **número** seguido de `:`.  
- Si la nota se refiere a un elemento sin numeración (títulos, acotaciones, prólogo, dramatis personae), se marca el término afectado con `@` seguido de `:`.  
- No se aplican estilos de Word, pero las cursivas se conservan.  

---

## 3.1 Notas asociadas a un verso numerado

Comienzan con el número de verso, seguido de `:`, y después el contenido de la nota redactado según los [*Criterios de edición de PROLOPE*](https://prolope.uab.cat/wp-content/uploads/2023/12/criterios_edicion_prolope.pdf) o aquellos elegidos.

<div class="ejemplo">
    <p>7: 7  <i>Niso</i>: rey de Megara, hermano de Egeo y padre de Escila. En la comedia de Lope no se menciona la ciudad de Megara sino que la acción se sitúa en Atenas, unificando así los episodios de Cila y Teseo (Sánchez Aguilar 2010:105).</p>
</div>

> Al procesar el archivo, feniX-ML asocia cada nota al verso correspondiente y la inserta al final de dicho verso en el XML.
{: .note }

---

## 3.2 Notas asociadas a elementos no numerados

Cuando la nota se refiere a un elemento sin numeración de verso, se usa el símbolo `@` antes del término afectado o antes del último del conjunto, seguido de `:`.

<div class="ejemplo">
    <p>@Píramo: <i>poema de Tisbe y Píramo</i>: se refiere a la <i>Fábula de Píramo y Tisbe</i> que escribió Juan de Vera y Figueroa, conde de la Roca.</p>
    <p>@poeta: Ovidio narró en el libro IV de sus <i>Metamorfosis</i> la historia de Píramo y Tisbe (vv. 55-166).</p>
</div>

> feniX-ML asocia estas notas al lugar del texto crítico donde se encuentra el mismo término marcado con `@`.
{: .note }

---

## Consejos finales
- No mezcles variantes y notas explicativas: cada tipo se gestiona en su archivo correspondiente.  
- Si un mismo término tiene varias notas, feniX-ML asigna identificadores únicos para diferenciarlas.

---
