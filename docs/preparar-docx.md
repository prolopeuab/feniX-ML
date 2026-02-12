---
layout: default
title: Preparación de archivos DOCX
nav_order: 3
has_children: true
---

# Preparación de archivos DOCX

Para generar una edición completa en feniX-ML, prepara estos documentos:

1. **Prólogo y texto crítico** (obligatorio)
2. **Aparato crítico** (opcional)
3. **Notas explicativas** (opcional)
4. **Metadatos** (opcional, recomendado)

## Reglas transversales importantes

- Trabaja sobre la plantilla de estilos del proyecto.
- Usa formato de entrada estricto en notas/aparato:
  - `NÚMERO:`
  - `NÚMERO+LETRA:` (ej. `329a:`)
  - `@PALABRA:`
  - `%PALABRA:`
- En el texto principal:
  - `@palabra` para notas.
  - `%palabra` para aparato.
  - `@%palabra` para ambos.

## Guía por archivo

- [1. Prólogo y texto crítico]({% link prologo-y-texto-critico.md %})
- [2. Aparato crítico]({% link aparato-critico.md %})
- [3. Notas explicativas]({% link notas.md %})
- [4. Metadatos]({% link metadatos.md %})

> Cada archivo se carga por separado en la interfaz de feniX-ML.
{: .note }
