---
layout: default
title: 1. Prólogo y texto crítico
parent: Preparar los archivos DOCX
nav_order: 1
---

# 1. Prólogo y texto crítico

Este archivo DOCX reúne dos partes fundamentales de la edición:  
el **prólogo o estudio introductorio** y el **texto crítico de la comedia**.

feniX-ML utiliza una plantilla con estilos personalizados que permiten aplicar marcas semánticas directamente en Word, además de una serie de símbolos mínimos. Estos estilos y símbolos serán interpretados por la herramienta y convertidos automáticamente en etiquetas XML-TEI.

---

## Estructura general del documento

El archivo debe contener, en este orden:

1. **Prólogo o estudio introductorio**
2. **Texto crítico de la comedia**

Ambas partes deben ir en un único archivo `.docx`, una a continuación de la otra.

Para preparar este archivo, deberás **copiar el contenido de tu edición (prólogo y texto crítico)** dentro de la plantilla de feniX-ML, que puedes descargar desde [aquí](https://github.com/prolopeuab/feniX-ML/ejemplos).

> ✴️ Es fundamental trabajar siempre sobre esta plantilla, ya que contiene los estilos necesarios que la aplicación reconoce para generar el XML correctamente.

Puedes pegar todo el contenido de una vez, o ir haciéndolo por secciones. Una vez dentro de la plantilla, deberás aplicar los estilos adecuados a cada parte del texto y símbolos siguiendo las instrucciones que se detallan a continuación.


---

## El prólogo

El prólogo debe ir al inicio del archivo `.docx`, **antes del título de la comedia**.

Cada sección del prólogo debe comenzar con una **almohadilla (`#`) sin espacio**, en una línea independiente. Este símbolo permite que la aplicación identifique la estructura interna del prólogo.

### Ejemplo

> #Prólogo  
> Texto introductorio del editor. Aquí puede aparecer texto en cursiva como *autoritas filológica*, que será conservado en la visualización final.

> #Estudio  
> Este es un ejemplo de cita textual:  
> «El arte nuevo consiste en decir lo que se piensa».

> Y también pueden incluirse versos si es necesario:  
> Ovejas sois, bien lo dice  
> quien al vulgo compara el sabio.

> #Sinopsis de la versificación

| Versos    | Estrofa            | Total |
|-----------|--------------------|--------|
| 1–50      | redondillas        | 50     |
| 51–100    | romance en -e-o    | 50     |
| **Total** |                    | 100    |

> #Resumen del argumento  
> Aquí va el resumen del argumento de la obra.

> #Nota onomástica  
> Explicación de los nombres propios presentes en la comedia.


Puedes incluir tantas secciones como necesites, siempre que cada título comience con `#`.


### Sinopsis de la versificación

La sección **"Sinopsis de la versificación"** debe presentarse en forma de tabla, como la que ya está incluida en el archivo de plantilla.  
No es necesario modificar su formato: solo debes actualizar los datos según tu edición.  
Este formato será reconocido y transformado correctamente en la edición digital.

---

### Notas en el prólogo

Las notas del prólogo (referencias, aclaraciones, bibliografía, etc.) deben insertarse como **notas al pie de página** en Word.

> Puedes hacerlo desde el menú `Referencias > Insertar nota al pie`, o utilizando el atajo de teclado `Ctrl + Alt + O`.

---

## Recomendaciones

- Puedes **copiar y pegar directamente** tu prólogo dentro de la plantilla, siempre colocándolo antes del título de la comedia.
- Cada sección del prólogo debe estar bien delimitada por una línea que comience con `#`, sin espacios.
- No es necesario aplicar el estilo `Prosa`: todo el contenido del prólogo se interpreta por defecto como texto en prosa.

---

### Casos especiales dentro del prólogo

- El programa **respeta la cursiva aplicada manualmente** en el texto del prólogo. Puedes usarla para destacar términos.  
- Si tu prólogo incluye **citas** textuales o **versos**, puedes aplicar los estilos `Cita` o `Verso`, respectivamente.
- Otros elementos como **imágenes**, **gráficos**, o **tablas** (distintas de la de versificación) **no serán interpretados automáticamente** y pueden generar errores en la conversión.  
  Te recomendamos evitarlos o consultar con un especialista en XML-TEI si necesitas incluirlos.





---

## 🎭 Aplicar los estilos del texto dramático

El archivo debe elaborarse utilizando la plantilla `plantilla.docx`, disponible en la carpeta de [ejemplos](https://github.com/prolopeuab/feniX-ML/ejemplos).  
Los estilos están diseñados para marcar visualmente los elementos del drama. A continuación, se indican los principales:

| **Estilo en Word**      | **Función**                                               | **Etiqueta XML generada**     |
|--------------------------|------------------------------------------------------------|--------------------------------|
| `Titulo_comedia`         | Título de la obra                                          | `<title>`                      |
| `Epigr_Dramatis`         | Epígrafe de la lista de personajes                         | `<castList>`                   |
| `Dramatis_lista`         | Nombre de cada personaje en la lista                       | `<castItem>`                   |
| `Epigr_Dedic`            | Epígrafe de la dedicatoria                                 | `<div type="dedicatoria">`     |
| `Prosa`                  | Párrafos no versificados                                   | `<p>`                          |
| `Acto`                   | Encabezado de cada acto                                    | `<div type="act">`             |
| `Personaje`              | Nombre del hablante al iniciar su intervención             | `<speaker>` dentro de `<sp>`  |
| `Verso`                  | Versos completos                                           | `<l>`                          |
| `Partido_inicial`        | Parte inicial de un verso partido                          | `<l part="I">`                 |
| `Partido_medio`          | Parte media de un verso partido                            | `<l part="M">`                 |
| `Partido_final`          | Parte final de un verso partido                            | `<l part="F">`                 |
| `Acot`                   | Acotaciones escénicas                                      | `<stage>`                      |

---

## 🎨 Guía visual del formato (opcional pero útil)

Cada estilo tiene una apariencia visual distinta en Word para facilitar su aplicación:

- Título: centrado, versalitas  
- Personajes: negrita + versalitas  
- Versos: en morado  
- Partes del verso partido: verde (inicio), aguamarina (medio), rojo (final)  
- Acotaciones: centradas y en cursiva

Esto te permite **verificar a simple vista** si los estilos han sido aplicados correctamente.

---

## ✍️ Notación especial para estrofas

Para indicar el comienzo de una nueva estrofa, escribe una línea que comience con `$` seguido del tipo de estrofa (sin espacios).  
Por ejemplo:
$redondilla
Esto se convertirá automáticamente en:
<milestone unit="stanza" type="redondilla"/>

## ⚠️ Casos particulares
Versos interrumpidos por acotación
Cuando un personaje habla, es interrumpido por una acotación, y luego continúa hablando, es necesario repetir el nombre del personaje antes de retomar el verso para mantener la estructura lógica del <sp>.

✴️ Esta repetición no se mostrará en la visualización final, pero es necesaria para el correcto procesado del XML.


✅ Consejos finales
Usa siempre la plantilla plantilla.docx y copia en ella el contenido que vayas a editar.

No modifiques manualmente los estilos: aplica los estilos desde el menú de estilos de Word.

Comprueba que no haya líneas de texto sin estilo aplicado: el validador de feniX-ML te avisará si hay errores.