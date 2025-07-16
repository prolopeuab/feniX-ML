# feniX-ML

Herramienta de transformación de archivos DOCX a XML-TEI a partir de ediciones críticas del teatro del Siglo de Oro.

Repositorio obsoleto desde julio de 2025. Visitar [@prolopeuab](https://github.com/prolope/feniX-ML) para acceder a la última versión de la herramienta.


## Instrucciones de compilado
```
.\.venv\Scripts\Activate.ps1
```

```
pyinstaller --onefile --windowed `
  --add-data "resources\CETEIcean.js;resources" `
  --add-data "resources\estilos.css;resources" `
  --add-data "resources\logo_prolope.png;resources" `
  --icon="resources\fenix.ico" `
  main.py
```
