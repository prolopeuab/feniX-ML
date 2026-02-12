---
layout: default
title: Primeros pasos e instalación
nav_order: 2
---

# Primeros pasos e instalación

## Descargar y ejecutar la app

feniX-ML se distribuye como ejecutable para Windows en la sección de [Releases del repositorio](https://github.com/prolopeuab/feniX-ML/releases).

El nombre del archivo puede variar según versión (por ejemplo, `feniXML.exe`).

1. Descarga el ejecutable.
2. Guárdalo en una carpeta local.
3. Ábrelo con doble clic.

## Requisitos del sistema

- **Windows 10 o superior**.
- Navegador web (Chrome, Edge, Firefox u otro) para la **vista previa HTML**.

No necesitas instalar Python para usar el ejecutable.

## Seguridad y avisos del sistema

Como ocurre con otros `.exe` distribuidos fuera de tiendas oficiales, algunos antivirus o SmartScreen pueden mostrar advertencias iniciales.

Si confías en la fuente del repositorio:

- Añade excepción en antivirus si fuera necesario.
- Ejecuta como administrador solo cuando el sistema lo pida.

## Archivos necesarios para trabajar

Para un flujo completo:

- Archivo principal `Prólogo y comedia` (obligatorio).
- `Notas` (opcional).
- `Aparato crítico` (opcional).
- `Metadatos` (opcional, recomendado).

Puedes revisar ejemplos en la carpeta [`ejemplos/`](https://github.com/prolopeuab/feniX-ML/tree/main/ejemplos).

## Uso con Python (macOS/Linux o entorno técnico)

La app está desarrollada en Python y el código fuente está en el repositorio. Si trabajas sin ejecutable de Windows, puedes ejecutar los scripts directamente con Python 3 y dependencias instaladas.

Referencia rápida en Windows (desde la raíz del proyecto):

```powershell
.\.venv\Scripts\Activate.ps1
python app\main.py
```
