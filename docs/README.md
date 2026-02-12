# Documentación de feniX-ML (`docs/`)

Este directorio contiene la documentación publicada con Jekyll + Just the Docs para feniX-ML.

## Estructura principal

- `index.md`: portada.
- `instalacion.md`: primeros pasos.
- `preparar-docx.md` y páginas hijas: preparación de archivos.
- `uso-app.md` y páginas hijas: carga, validación, exportación.
- `resolucion-problemas.md`: incidencias comunes.
- `creditos.md`: créditos y contacto.

## Ejecutar la documentación en local

Desde `docs/`:

```bash
bundle install
bundle exec jekyll serve
```

Sitio local por defecto: `http://localhost:4000`.

## Convención de capturas

Base:

- `docs/assets/images/capturas/uso-app/`
- `docs/assets/images/capturas/preparar-docx/`
- `docs/assets/images/capturas/resolucion/`

Nombres recomendados:

- `01-pantalla-principal.png`
- `02-carga-archivos.png`
- etc.

En Markdown, insertar la ruta final aunque la imagen aún no exista y añadir debajo:

```markdown
*Captura pendiente de insertar.*
```

## Guía rápida de edición

1. Mantener contenido alineado con comportamiento real de:
   - `app/gui.py`
   - `app/tei_backend.py`
   - `app/visualizacion.py`
2. Evitar promesas no implementadas.
3. Mantener redacción simple y directa.

## Checklist antes de publicar

- Enlaces internos correctos.
- Sin páginas vacías de navegación principal.
- Sintaxis de anotaciones consistente (`@`, `%`, `@%`).
- Build de Jekyll sin errores.
