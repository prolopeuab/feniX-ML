# Proceso de Releases en GitHub (feniX-ML)

Este proyecto ya incluye un flujo automático en:

- `.github/workflows/release.yml`

Cuando hagas push de un tag `v*` (por ejemplo `v1.0.0`), GitHub:

1. compila `feniXML.exe` en Windows,
2. genera `feniXML.exe.sha256.txt`,
3. publica una Release con ambos archivos adjuntos.

## Primera release estable (paso a paso)

### 1) Asegura estado estable en `main`

- Código y docs listos.
- Commit final hecho.
- Push a remoto.

```powershell
git checkout main
git pull
git status
```

### 2) Crea y sube tag de versión

Usa versionado semántico:

- `v1.0.0` (estable mayor)
- `v1.0.1` (fix)
- `v1.1.0` (nueva funcionalidad compatible)
- `v1.1.0-beta.1` (pre-release)

```powershell
git tag -a v1.0.0 -m "feniX-ML v1.0.0"
git push origin v1.0.0
```

### 3) Revisa la ejecución automática

En GitHub:

- `Actions` -> workflow `Build And Publish Release`
- Espera a que termine en verde.

### 4) Revisa la release publicada

En GitHub:

- `Releases` -> `v1.0.0`
- Verifica adjuntos:
  - `feniXML.exe`
  - `feniXML.exe.sha256.txt`

## Verificación rápida del binario antes de anunciar

1. Descarga `feniXML.exe` desde la release.
2. Ejecuta en un entorno limpio.
3. Prueba flujo básico:
   - abrir app,
   - cargar archivo principal,
   - validar,
   - vista previa XML/HTML,
   - exportar XML.

## Flujo recomendado en adelante

1. Mantener `main` como estable.
2. Hacer trabajo en ramas (`feature/*`, `fix/*`).
3. Integrar a `main` solo lo que esté listo.
4. Publicar release solo con tag.

## Notas útiles

- Si el tag contiene guion (ej. `v1.2.0-rc.1`), la release se marca como **pre-release** automáticamente.
- Si necesitas rehacer una versión, crea un nuevo tag (`v1.0.1`) en lugar de reutilizar el mismo.
