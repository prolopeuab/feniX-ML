# ==========================================
# feniX-ML: Utilidad para configurar el icono en Windows
# Solución para mostrar correctamente el icono en explorador, barra de tareas y ventana
# ==========================================

import sys
import os
import ctypes
import tkinter as tk
from pathlib import Path

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        # Si está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Si se ejecuta como script, usar el directorio del archivo actual
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def set_windows_icon(root: tk.Tk):
    """
    Configura el icono de la aplicación en Windows para:
    - Explorador de archivos
    - Barra de tareas
    - Ventana de la aplicación
    """
    # AppUserModelID: fija el icono de la barra de tareas y el "grouping"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("uab.prolope.fenixML")
    except Exception:
        pass  # No está en Windows o no tiene permisos

    # Icono de la ventana (título)
    ico_path = resource_path("resources/icon.ico")
    try:
        root.iconbitmap(default=ico_path)
    except Exception:
        pass  # Si no se encuentra el icono, usa el predeterminado
