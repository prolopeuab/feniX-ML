---
layout: default
title: Instalación
nav_order: 2
---

# Instalación

## Descargar y ejecutar la app

feniX-ML se distribuye como ejecutable para Windows en la sección de [Releases del repositorio](https://github.com/prolopeuab/feniX-ML/releases).

> Descarga siempre desde los releases del repositorio oficial para evitar ejecutables alterados.
{: .important }

Encontrarás dos opciones:

- `feniXML.exe` (ejecutable directo).
- `.zip` (incluye ejecutable y plantillas necesarias).

![Releases en GitHub]({{ '/assets/images/capturas/releases.png' | relative_url }}){: .img-50 }

1. Descarga el ejecutable o el `.zip`.
2. Guárdalo en una carpeta local y descomprime si es necesario.
3. Abre `feniXML.exe`.

## Requisitos del sistema

- **Windows 10 o superior**.
- Navegador web (Chrome, Edge, Firefox u otro) para la **vista previa HTML**.

> No necesitas instalar Python para usar el ejecutable.
{: .tip }

## Verificación rápida tras instalar

- La aplicación abre sin errores.
- Puedes cargar un DOCX de ejemplo de [`ejemplos/`](https://github.com/prolopeuab/feniX-ML/tree/main/ejemplos).
- Puedes generar la vista previa HTML local.

## Seguridad y avisos del sistema

Como ocurre con otros `.exe` distribuidos fuera de tiendas oficiales, algunos antivirus o SmartScreen pueden mostrar advertencias iniciales.

> Si aparece SmartScreen, comprueba que el archivo proviene del repositorio oficial antes de continuar.
> Ejecuta como administrador solo cuando Windows lo solicite de forma explícita.
{: .warning }

## Qué necesitarás después

Para el flujo completo de trabajo, consulta:

- [Preparación de archivos DOCX]({% link preparar-docx.md %})
- [Uso de la app]({% link uso-app.md %})

## Uso con Python (macOS/Linux o entorno técnico)

La app está desarrollada en Python y el código fuente está en el repositorio. Si trabajas sin ejecutable de Windows, puedes ejecutar los scripts directamente con Python 3 y dependencias instaladas.

Referencia rápida en Windows (desde la raíz del proyecto):

```powershell
.\.venv\Scripts\Activate.ps1
python app\main.py
```
