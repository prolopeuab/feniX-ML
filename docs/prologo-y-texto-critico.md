---
layout: default
title: 1. Prólogo y texto crítico
parent: Preparar los archivos DOCX
nav_order: 1
---

# 1. Prólogo y texto crítico

Este archivo DOCX reúne dos partes fundamentales de la edición:  
el **prólogo o estudio introductorio** y el **texto crítico de la comedia**.

feniX-ML utiliza una [plantilla](https://github.com/prolopeuab/feniX-ML/ejemplos) con estilos personalizados que permiten aplicar marcas semánticas directamente en Word, además de una serie de símbolos mínimos. Estos estilos y símbolos serán interpretados por la herramienta y convertidos automáticamente en etiquetas XML-TEI.

---

## Estructura general del documento

El archivo debe contener, en este orden:

1. **Prólogo o estudio introductorio**
2. **Texto crítico de la comedia**

Ambas partes deben ir en un único archivo `.docx`, una a continuación de la otra.

Para preparar este archivo, deberás **copiar el contenido de tu edición (prólogo y texto crítico)** dentro de la plantilla de feniX-ML, que puedes descargar desde [aquí](https://github.com/prolopeuab/feniX-ML/ejemplos).

> Es fundamental trabajar siempre sobre esta plantilla, ya que contiene los estilos necesarios que la aplicación reconoce para generar el XML correctamente.
{: .important }

Puedes pegar todo el contenido de una vez, o ir haciéndolo por secciones. Una vez dentro de la plantilla, deberás aplicar los estilos adecuados a cada parte del texto y símbolos siguiendo las instrucciones que se detallan a continuación.


---

## 1.1 El prólogo

El prólogo debe ir al inicio del archivo `.docx`, **antes del título de la comedia**.

### Estructura mínima

Para que el prólogo sea reconocido correctamente por la herramienta, debe cumplir estos requisitos mínimos:

- **Estar situado al inicio del documento**, antes del título de la comedia.
- **Incluir al menos una sección**, encabezada por una línea que comience con `#` (sin espacio).
- Cada sección debe comenzar en una **línea nueva**, y el símbolo `#` debe ir seguido directamente del nombre de la sección (sin espacio).
- Todo el contenido del prólogo se interpreta por defecto como texto en prosa, por lo que no es necesario utilizar el estilo `Prosa` incluido en la plantilla (ver la utilidad de este estilo [aquí](http://prolopeuab.github.io/feniX-ML/prologo-y-texto-critico#los-estilos)).


#### Ejemplo:
<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.05em;">
  <p>#Prólogo<br>
  Texto introductorio del editor.</p>

  <p>#Resumen del argumento<br>
  Aquí va el resumen del argumento...</p>
</div>

#### Secciones
Puedes incluir tantas secciones como quieras. Algunas habituales y las que reconoce feniX-ML por defecto son:
  - `#Prólogo`
  - `#Estudio`
  - `#Sinopsis de la versificación`
  - `#Resumen del argumento`
  - `#Nota onomástica`
  
### Sinopsis de la versificación
Esta sección debe presentarse en forma de tabla, como la que ya está incluida en el archivo de plantilla.  
No es necesario modificar su formato: solo debes actualizar los datos según tu edición.  

### Notas en el prólogo
Las notas del prólogo (referencias, aclaraciones, bibliografía, etc.) deben insertarse como **notas al pie de página** en Word.

> Puedes hacerlo desde el menú `Referencias > Insertar nota al pie`, o utilizando el atajo de teclado `Ctrl + Alt + O`.
{: .tip }

### Casos especiales

Además de su estructura mínima, el prólogo puede enriquecerse con distintos elementos marcados con estilo (ver lista completa [aquí](http://prolopeuab.github.io/feniX-ML/prologo-y-texto-critico#los-estilos)):

- **Citas textuales** → aplica el estilo `Cita`  
- **Versos** → aplica el estilo `Verso`  
- **Cursivas** → cualquier cursiva aplicada en Word se conservará  
  
> Recuerda que elementos como imágenes, gráficos o tablas que no sean la de versificación **no serán procesados automáticamente**. Si los incluyes, pueden provocar errores en el archivo XML generado.   Te recomendamos evitarlos o consultar con un especialista en XML-TEI si necesitas incluirlos.
{: .warning }


### Ejemplo de prólogo

<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.05em;">

<p>#Prólogo<br>
Texto introductorio del editor. Aquí puede aparecer texto en <em>cursiva</em>, que será conservado en la visualización final.<sup style="font-size: 0.75em;">1</sup>
</p>

<p>También pueden incluirse versos si es necesario, usando el estilo correspondiente (<code>Verso</code>):</p>

<p style="margin-left: 2em; line-height: 1.5;">
  Hoy entrambos los poseo,<br>
  pues he tenido, Feniso,<br>
  con la vitoria de Niso,<br>
  la venganza de Androgeo.
</p>

<p>#Sinopsis de la versificación<br>
Siguiendo el formato de tabla de la plantilla:</p>

<table>
  <thead>
    <tr><th>Versos</th><th>Estrofa</th><th>Total</th></tr>
  </thead>
  <tbody>
    <tr><td>1–8</td><td>redondillas</td><td>8</td></tr>
    <tr><td>9–142</td><td>romance en -e-o</td><td>134</td></tr>
  </tbody>
</table>

<p>#Resumen del argumento<br>
Aquí va el resumen del argumento de la obra.</p>

<p>#Nota onomástica<br>
Explicación de los nombres propios presentes en la comedia.</p>

<hr style="border: none; border-top: 1px solid #aaa; margin-top: 2em;"/>

<p style="font-size: 0.85em;"><sup>1</sup> Las notas deben insertarse como notas al pie en Word.</p>

</div>

---


## 1.2 El texto crítico

Tras el prólogo comienza el cuerpo principal de la edición crítica. Este puede incluir las siguientes secciones:
- Título de la comedia
- Dedicatoria (si la hay)
- Lista de personajes (dramatis personae)
- Texto dramático (actos, intervenciones, acotaciones)


### Los estilos
Para marcar semáticamente el texto crítico se utilizan los estilos predefinidos en la plantilla de Word de feniX-ML. A continuación, se detalla la correspondencia entre estos estilos y las etiquetas XML-TEI generadas automáticamente por el programa:


| **Estilo en Word**      | **Función**                                               | **Etiqueta XML generada**     |
|--------------------------|------------------------------------------------------------|--------------------------------|
| `Titulo_comedia`         | Título de la obra                                          | `<title>`                      |
| `Epigr_Dramatis`         | Epígrafe de la lista de personajes                         | `<castList>`                   |
| `Dramatis_lista`         | Nombre de cada personaje en la lista                       | `<castItem>`                   |
| `Epigr_Dedic`            | Epígrafe de la dedicatoria                                 | `<div type="dedicatoria">`     |
| `Prosa`                  | Párrafos no versificados dentro de una intervención       | `<p>`                          |
| `Acto`                   | Encabezado de cada acto                                    | `<div type="act">`             |
| `Personaje`              | Nombre del hablante al iniciar su intervención             | `<speaker>` dentro de `<sp>`  |
| `Verso`                  | Versos completos                                           | `<l>`                          |
| `Partido_inicial`        | Parte inicial de un verso partido                          | `<l part="I">`                 |
| `Partido_medio`          | Parte media de un verso partido                            | `<l part="M">`                 |
| `Partido_final`          | Parte final de un verso partido                            | `<l part="F">`                 |
| `Acot`                   | Acotaciones escénicas                                      | `<stage>`                      |


#### Guía visual rápida

Cada estilo tiene una apariencia visual distinta en Word para facilitar su aplicación y revisión:

| Elemento               | Apariencia en Word   |
| ---------------------- | -------------------- |
| Título de la comedia   | Centrado, versalitas |
| Nombre del personaje   | Negrita, versalitas  |
| Verso completo         | Texto morado         |
| Verso partido (inicio) | Verde                |
| Verso partido (medio)  | Aguamarina           |
| Verso partido (final)  | Rojo                 |
| Acotación escénica     | Cursiva, centrada    |


Esto te permite **verificar a simple vista** si los estilos han sido aplicados correctamente.

---

### Notas: variantes y explicativas
El sistema de marcado de feniX-ML acepta dos tipos de notas: las de aparato crítico y las explicativas o filológicas. Su contenido se redacta en archivos independientes (ver [Aparato crítico](https://prolopeuab.github.io/feniX-ML/aparato-critico) y [Notas explicativas](https://prolopeuab.github.io/feniX-ML/notas)), pero en el texto crítico debe marcarse el punto de referencia de cada llamada.

#### Versos numerados
Si la nota (de aparato o explicativa) refiere un verso o término en un verso, no debe añadirse nada. El programa es capaz de asociar cada nota con el verso correspondiente gracias al número de verso.

#### Elementos no numerados
Si la nota (de aparato o explicativa) refiere a un elemento sin numeración de verso (por ejemplo, términos en títulos, acotaciones, prólogo o dramatis personae), se utiliza el símbolo `@` para indicar el punto de referencia de la siguiente manera:

```
El breve poema de Tisbe y @Píramo, aunque dilatado en la majestad...
```

En este caso, la nota afecta a "poema de Tisbe y Píramo", por lo que se coloca antes del último término: `@Píramo`.


```
Salen Teseo, @Albante y Fineo, criado de Teseo 
```

En este caso, la nota afecta a "Albante", por lo que se coloca antes del término: `@Albante`.


> No es necesario añadir ningún otro símbolo o estilo: feniX-ML enlaza automáticamente esta marca con la nota correspondiente en el archivo adecuado.
{: .note }


### Formas estróficas
Para indicar el comienzo de una nueva estrofa, escribe una línea que comience con `$` seguida del tipo de estrofa, sin espacios:

```
$redondilla
```

Esto se convertirá automáticamente en:

```
<milestone unit="stanza" type="redondilla"/>
```

### Casos particulares
#### Estilos en la dedicatoria
En la dedicatoria, si la hubiera, solo debe usarse estilos para el epígrafe `Epigr_Dedic` y para los versos, si los hubiera. El resto del contenido se considera automáticamente prosa, por lo que no es necesario aplicar el estilo `Prosa`, igual que ocurre en el prólogo

#### Versos interrumpidos por acotación
En los textos teatrales del Siglo de Oro, puede ocurrir que los versos de un determinado personaje se vean interrumpidos por una acotación escénica, y que, tras ella, el mismo personaje continúe hablando sin que su nombre vuelva a aparecer antes de los nuevos versos (se sobreentiende que se trata de la misma intervención hablada). En estos casos, **será necesario añadir manualmente el nombre del personaje** antes de sus versos.

> Esta repetición no se mostrará en la visualización final, pero es necesaria para el correcto procesado del XML y generar una codificación TEI semánticamente correcta.
{: .note }

#### Ejemplo:
<div style="border: 1px solid #ccc; padding: 1em; background-color: #f9f9f9; font-family: 'Garamond', serif; font-size: 1.1em;">
  <p>
    <span style="font-variant: small-caps; font-weight: bold;">Personaje</span><br>
    <span style="color: #6a1b9a;">Verso 1</span><br>
    <span style="color: #6a1b9a;">Verso 2</span><br>
    <span style="color: #6a1b9a;">Verso 3</span><br>
    <span style="font-style: italic; display: block; text-align: center;">Acotación que interrumpe los versos</span>
    <span style="font-variant: small-caps; font-weight: bold;">Personaje</span> (repetición)<br>
    <span style="color: #6a1b9a;">Verso 4</span><br>
    <span style="color: #6a1b9a;">Verso 5</span><br>
    <span style="color: #6a1b9a;">Verso 6</span>
  </p>
</div>


## Consejos finales
- Usa siempre la plantilla `plantilla.docx` y copia en ella el contenido que vayas a editar.
- No modifiques manualmente los estilos: aplica los estilos desde el menú de estilos de Word.
- Comprueba que no haya líneas de texto sin estilo aplicado dentro del texto crítico, pero no te preocupes, el validador de **feniX-ML** te avisará si detecta errores.