# feniX-ML

.\.venv\Scripts\Activate.ps1

pyinstaller --onefile --windowed `
  --add-data "resources\CETEIcean.js;resources" `
  --add-data "resources\estilos.css;resources" `
  main.py
