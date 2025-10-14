# ==========================================
# feniX-ML: Lanzador de la interfaz gráfica para la conversión automática de DOCX a TEI/XML
# Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde
# Grupo de investigación PROLOPE, Universitat Autònoma de Barcelona
# Descripción: Archivo principal de entrada. Inicializa la configuración de la aplicación
#              y lanza la interfaz gráfica (GUI) para seleccionar archivos, validar, convertir
#              y previsualizar ediciones críticas teatrales en formato DOCX a XML-TEI.
# Este script debe utilizarse junto a tei_backend.py, visualizacion.py y gui.py.
# ==========================================

import ctypes
import tkinter as tk

# Hacer que la app sea DPI-aware en Windows 10/11 para evitar desenfoque en pantallas HiDPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Escalado adicional para fuentes e interfaz (ajustable según necesidad) sin mostrar ventana
root = tk.Tk()
root.withdraw()
root.tk.call('tk', 'scaling', 1)
root.destroy()

from gui import main_gui

# ==== PUNTO DE ENTRADA DE LA APLICACIÓN ====
if __name__ == "__main__":
    # Lanza la interfaz gráfica principal de feniX-ML
    main_gui()
