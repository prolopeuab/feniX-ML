# feniX-ML

**feniX-ML** es una aplicación de escritorio con interfaz gráfica que permite convertir ediciones críticas de teatro del Siglo de Oro en formato DOCX a archivos en formato XML-TEI, listos para su publicación digital. Ha sido desarrollada por el grupo de investigación **PROLOPE** (Universitat Autònoma de Barcelona) como parte del proyecto de la *Biblioteca Digital PROLOPE*.

## ¿Qué hace feniX-ML?
- Convierte automáticamente textos teatrales en DOCX (prologados, anotados y con aparato crítico) a TEI/XML.
- Permite cargar y validar múltiples archivos DOCX: texto principal, notas, aparato crítico y metadatos.
- Genera un archivo TEI válido y completo, incluyendo `teiHeader`.
- Ofrece vistas previas en XML plano y en HTML interactivo (renderizado con CETEIcean.js).

## Estructura del repositorio
```
feniX-ML/
│
├── app/ ← Código fuente en Python (.py) y ejecutable
│ ├── main.py ← Lanzador de la aplicación
│ ├── gui.py ← Interfaz gráfica (Tkinter)
│ ├── tei_backend.py ← Lógica de conversión DOCX → TEI
│ └── visualizacion.py ← Vista previa (XML / HTML)
│
├── tests/ ← Plantillas y archivos DOCX de prueba
├── versiones/ ← Versiones de los archivos Python anteriores
└── README.md ← Este archivo
````

## Instrucciones de compilado a partir de los archivos Python
Activa tu entorno virtual:

```
.\.venv\Scripts\Activate.ps1
```

Ejecuta el siguiente comando para generar el ejecutable .exe:

```
pyinstaller --onefile --windowed `
  --add-data "resources\CETEIcean.js;resources" `
  --add-data "resources\estilos.css;resources" `
  --add-data "resources\logo_prolope.png;resources" `
  --icon="resources\fenix.ico" `
  main.py
```
El ejecutable se generará en la carpeta dist/.

## Créditos
Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.
Grupo de investigación PROLOPE · Universitat Autònoma de Barcelona · 2025

## Licencia
Este software se distribuye bajo una licencia Creative Commons BY-NC-SA 4.0.
