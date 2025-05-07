import ctypes
import tkinter as tk

# Hacer que la app sea DPI-aware en Windows 10/11
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Escalado adicional para fuentes e interfaz (ajustable)
tk.Tk().tk.call('tk', 'scaling', 1.75)

from gui import main_gui

if __name__ == "__main__":
    main_gui()
