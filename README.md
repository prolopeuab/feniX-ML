# feniX-ML

**feniX-ML** es una aplicación de escritorio con interfaz gráfica que permite convertir ediciones críticas de teatro del Siglo de Oro en formato DOCX a archivos en formato XML-TEI, listos para su publicación digital. Ha sido desarrollada por Anna Abate, Emanuele Lebofe y David Merino Recalde en el grupo de investigación **PROLOPE** (Universitat Autònoma de Barcelona) como parte del proyecto de la *Biblioteca Digital PROLOPE*.

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
├── docs/ ← Documentación técnica, accesible desde [prolopeuab.github.io/feniX-ML](https://prolopeuab.github.io/feniX-ML)
├── ejemplos/ ← Plantillas y archivos DOCX de prueba
├── versiones/ ← Versiones de los archivos Python anteriores
└── README.md ← Este archivo
````

## Instrucciones de compilado a partir de los archivos Python

**Nota**: Asegúrate de estar en el directorio raíz del proyecto (`C:\...\feniX-ML`).

Activa tu entorno virtual:

```
.\.venv\Scripts\Activate.ps1
```

Limpia las carpetas de compilaciones anteriores (opcional pero recomendado):

```
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue
```

Ejecuta el siguiente comando para generar el ejecutable .exe:

```
pyinstaller --onefile --windowed `
  --name "feniXML" `
  --add-data "app\resources\CETEIcean.js;resources" `
  --add-data "app\resources\estilos.css;resources" `
  --add-data "app\resources\logo_prolope.png;resources" `
  --add-data "app\resources\logo.png;resources" `
  --add-data "app\resources\icon.ico;resources" `
  --icon="app\resources\icon.ico" `
  app\main.py
```

**Nota sobre el icono**: El ejecutable incluye configuración especial (AppUserModelID) para que el icono se muestre correctamente en el explorador de archivos, la barra de tareas y la ventana de la aplicación en Windows. Si tras recompilar aparece el icono antiguo, reinicia el Explorador de Windows (`taskkill /f /im explorer.exe; Start-Process explorer.exe`).

El ejecutable se generará en `dist\feniXML.exe` en el directorio raíz del proyecto.

## Créditos
Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.
Grupo de investigación PROLOPE · Universitat Autònoma de Barcelona · 2025

## Licencia
Este software se distribuye bajo una licencia Creative Commons BY-NC-SA 4.0.
