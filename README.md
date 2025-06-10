# feniX-ML

.\.venv\Scripts\Activate.ps1


# EJECUTABLE
pyinstaller --onefile --windowed `
  --add-data "resources\CETEIcean.js;resources" `
  --add-data "resources\estilos.css;resources" `
  --add-data "resources\logo_prolope.png;resources" `
  --icon="resources\fenix.ico" `
  main.py

