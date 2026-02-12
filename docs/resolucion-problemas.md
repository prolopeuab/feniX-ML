---
layout: default
title: Resolución de problemas
nav_order: 5
has_children: false
---

# Resolución de problemas

## 1) "Estilo no válido"

**Síntoma**
- Mensajes `❌ Estilo no válido: ...` en validación.

**Causa habitual**
- Se aplicó un estilo no contemplado para el cuerpo de la obra.
- Error tipográfico en estilo (por ejemplo, `Partido_incial` en lugar de `Partido_inicial`).

**Solución rápida**
- Reaplica el estilo correcto de la plantilla Word.
- Revalida antes de exportar.

## 2) "Líneas sin estilo detectadas"

**Síntoma**
- Mensaje `❌ LÍNEAS SIN ESTILO DETECTADAS (...)`.

**Causa habitual**
- Párrafos en `Normal` dentro del cuerpo textual.

**Solución rápida**
- Localiza los fragmentos indicados por validación.
- Asigna estilo semántico correcto (`Verso`, `Prosa`, `Acot`, etc.).

## 3) "Verso partido incompleto"

**Síntoma**
- Avisos sobre secuencia incorrecta de versos partidos.

**Causa habitual**
- Existe `Partido_inicial` sin `Partido_final`.
- Hay `Partido_medio`/`Partido_final` sin inicio correcto.

**Solución rápida**
- Verifica secuencia completa: `Partido_inicial` -> (`Partido_medio` opcional) -> `Partido_final`.

## 4) "Laguna" o "verso con corchetes"

**Síntoma**
- Avisos `⚠️ LAGUNA DETECTADA` o `⚠️ VERSO CON CORCHETES DETECTADO`.

**Criterio práctico**
- Usa `Laguna` cuando la extensión perdida es incierta.
- Usa `Verso` con corchetes cuando representa un verso concreto que debe contar en numeración.

## 5) Formato de notas/aparato incorrecto

**Síntoma**
- `❌ Formato incorrecto en archivo ...`.

**Formato válido por párrafo**
- `NÚMERO:`
- `NÚMERO+LETRA:` (ej. `329a:`)
- `@PALABRA:`
- `%PALABRA:`

**Recordatorio de marcadores en texto principal**
- `@palabra` -> nota explicativa.
- `%palabra` -> aparato crítico.
- `@%palabra` -> ambas.

![Ejemplo de mensaje de error de validación](assets/images/capturas/resolucion/01-error-validacion.png)

*Captura pendiente de insertar.*
