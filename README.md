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
├── app/ ← Código fuente en Python (.py) y recursos de la aplicación
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

Este paso sirve para probar localmente la generación del ejecutable. En una release oficial, GitHub Actions repetirá este proceso automáticamente al subir el tag.

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

## Criterio de versionado

feniX-ML sigue un criterio simple inspirado en SemVer: `vX.Y.Z`.

- `Z` (parche): correcciones de errores, ajustes visuales o internos, mejoras de documentación y recompilados del ejecutable sin capacidades nuevas relevantes para la persona usuaria.
- `Y` (minor): nuevas funcionalidades compatibles, como soporte para nuevos estilos de Word, nuevas estructuras TEI, validaciones adicionales o mejoras visibles de uso sin romper flujos anteriores.
- `X` (major): cambios incompatibles en el flujo de trabajo, en las convenciones de marcado en Word o en la estructura de salida TEI que obliguen a adaptar documentos o procesos existentes.

Regla práctica para decidir:

- Si solo hemos corregido o afinado algo ya existente, subimos parche.
- Si hemos añadido capacidades nuevas compatibles, subimos minor.
- Si rompemos compatibilidad con documentos o salidas previas, subimos major.

Pre-releases:

- Usa sufijos como `-rc1` o `-beta1` cuando quieras probar una versión antes de marcarla como estable.

## Cómo publicar una nueva release

Las releases oficiales de feniX-ML se publican a partir de tags de Git.  
El flujo previsto es:

```text
main estable → tag vX.Y.Z → GitHub Actions → release oficial
```

GitHub Actions se encarga de compilar el ejecutable y adjuntarlo a la release. Por tanto, no es necesario subir manualmente `dist\feniXML.exe` al repositorio.

### 1. Decidir el número de versión

Antes de publicar una release, decide si el cambio corresponde a una versión de parche, minor o major siguiendo el criterio de versionado anterior.

Ejemplos:

```text
v1.0.1     # parche
v1.1.0     # minor
v2.0.0     # major
v1.1.0-rc1 # release candidata
```

### 2. Actualizar la versión interna de la aplicación

Actualiza la versión declarada dentro del código de la aplicación para que coincida con el tag que se va a publicar.

Por ejemplo, si la nueva release será:

```text
v1.1.0
```

la versión interna de la aplicación debe quedar como:

```text
1.1.0
```

### 3. Comprobar que `main` está estable

Antes de crear el tag, revisa que la rama `main` contiene todos los cambios necesarios y que no quedan archivos pendientes.

```bash
git checkout main
git pull origin main
git status
```

Si hay cambios pendientes, añádelos y crea el commit final:

```bash
git add .
git commit -m "Prepare release vX.Y.Z"
git push origin main
```

Sustituye `vX.Y.Z` por el número real de la versión.

Ejemplo:

```bash
git commit -m "Prepare release v1.1.0"
```

### 4. Crear el tag desde `main`

Crea el tag con el formato correspondiente:

```bash
git tag vX.Y.Z
```

Ejemplo:

```bash
git tag v1.1.0
```

Para una release candidata:

```bash
git tag v1.1.0-rc1
```

### 5. Subir el tag a GitHub

Sube el tag al repositorio remoto:

```bash
git push origin vX.Y.Z
```

Ejemplo:

```bash
git push origin v1.1.0
```

Al subir el tag, GitHub Actions iniciará automáticamente el proceso de compilación y publicación de la release.

### 6. Revisar la release en GitHub

Una vez finalizada la acción automática, comprueba en GitHub que:

* la acción terminó correctamente;
* se creó una nueva release con el tag correspondiente;
* la release incluye el ejecutable `feniXML.exe`;
* la versión interna de la aplicación coincide con el número de la release.

### Secuencia rápida

Para publicar una release estable:

```bash
git checkout main
git pull origin main
git status
git add .
git commit -m "Prepare release vX.Y.Z"
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

Para publicar una release candidata:

```bash
git checkout main
git pull origin main
git status
git add .
git commit -m "Prepare release vX.Y.Z-rc1"
git push origin main
git tag vX.Y.Z-rc1
git push origin vX.Y.Z-rc1
```


## Créditos
Desarrollado por Anna Abate, Emanuele Leboffe y David Merino Recalde.
Grupo de investigación PROLOPE · Universitat Autònoma de Barcelona · 2025

## Licencia
Este software se distribuye bajo una licencia Creative Commons BY-NC-SA 4.0.
