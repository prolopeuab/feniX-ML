# Proceso de Releases en GitHub (feniX-ML)

Flujo automático en:

- `.github/workflows/release.yml`

Cuando se hace push de un tag `v*` (por ejemplo `v1.0.0`), GitHub:

1. compila `feniXML.exe` en Windows,
2. genera `feniXML.exe.sha256.txt`,
3. genera `feniXML+plantillas.zip` con:
   - `feniXML.exe`
   - `plantillas/plantilla_prologoycomedia.docx`
   - `plantillas/plantilla_notas.docx`
   - `plantillas/plantilla_aparato.docx`
   - `plantillas/plantilla_metadatos.docx`
4. publica una Release con los binarios y checksums adjuntos.

La compilación usa el mismo comando de PyInstaller documentado en `README.md`.

## Proceso

### 1) Asegurar estado estable en `main`

- Código y docs listos.
- Commit final hecho.
- Push a remoto.

```powershell
git checkout main
git pull
git status
```

### 2) Crear y subir tag de versión

Versionado semántico:

- `v1.0.0` (estable mayor)
- `v1.0.1` (fix)
- `v1.1.0` (nueva funcionalidad compatible)
- `v1.1.0-beta.1` (pre-release)

```powershell
git tag -a v1.0.0 -m "feniX-ML v1.0.0"
git push origin v1.0.0
```

### 3) Revisar la ejecución automática

En GitHub:

- `Actions` -> workflow `Build And Publish Release`

### 4) Revisar la release publicada

En GitHub:

- `Releases` -> `v1.0.0`
- Verificar adjuntos:
  - `feniXML.exe`
  - `feniXML.exe.sha256.txt`
  - `feniXML+plantillas.zip`
  - `feniXML+plantillas.zip.sha256.txt`

## Verificación rápida del binario

1. Descargar `feniXML.exe` desde la release.
2. Ejecutar en un entorno limpio.
3. Probar flujo básico:
   - abrir app,
   - cargar archivo principal,
   - validar,
   - vista previa XML/HTML,
   - exportar XML.

## Flujo

1. Mantener `main` como estable.
2. Hacer trabajo en ramas (`feature/*`, `fix/*`).
3. Integrar a `main`.
4. Publicar release con tag.

## Notas útiles

- Si el tag contiene guion (ej. `v1.2.0-rc.1`), la release se marca como **pre-release** automáticamente.
- El workflow valida que el commit del tag pertenezca a `main`; si no, la release falla.
- Para rehacer una versión, crear un nuevo tag (`v1.0.1`) en lugar de reutilizar el mismo.
