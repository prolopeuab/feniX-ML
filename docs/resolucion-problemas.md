---
layout: default
title: Resolución de problemas
nav_order: 5
has_children: false
---

# Resolución de problemas

## 1) "Debe seleccionar un archivo principal"

**Síntoma**
- La app muestra el aviso en `Validación`, `Vista previa` o `Conversión`.

**Causa habitual**
- No se cargó `Prólogo y comedia` en el primer bloque de la interfaz.
- El archivo se movió o renombró y la ruta ya no es válida.

**Solución rápida**
- Vuelve a seleccionar el archivo principal en `Carga de archivos`.
- Repite la acción (`Validar marcado`, `Vista previa` o `Generar archivo XML-TEI`).

## 2) "❌ Estilo no válido: ..."

**Síntoma**
- Mensajes como `❌ Estilo no válido: ...`.

**Causa habitual**
- Se aplicó un estilo no contemplado para el cuerpo de la obra.
- Error tipográfico en el nombre del estilo (por ejemplo, `Partido_incial` en lugar de `Partido_inicial`).

**Solución rápida**
- Reaplica estilos de la plantilla oficial (`Verso`, `Prosa`, `Acot`, `Acto`, etc.).
- Revalida para confirmar que el aviso desaparece.

## 3) "❌ LÍNEAS SIN ESTILO DETECTADAS (...)"

**Síntoma**
- Mensaje `❌ LÍNEAS SIN ESTILO DETECTADAS (...)`.

**Causa habitual**
- Hay párrafos en estilo `Normal` (o sin estilo) dentro del cuerpo de la obra.
- Suele ocurrir al copiar/pegar texto desde otro documento.

**Solución rápida**
- Localiza las líneas indicadas por validación.
- Asigna un estilo semántico válido a cada una.

## 4) "❌ (...) VERSO(S) PARTIDO(S) INCOMPLETO(S)"

**Síntoma**
- Aviso de versos partidos incompletos.

**Causa habitual**
- Existe `Partido_inicial` sin `Partido_final`.
- Hay `Partido_medio` o `Partido_final` sin arranque correcto.

**Solución rápida**
- Revisa la secuencia completa: `Partido_inicial` -> (`Partido_medio` opcional) -> `Partido_final`.
- Asegura que todos los tramos pertenecen al mismo verso.

## 5) "⚠️ DESAJUSTE EN LA NUMERACIÓN DE VERSOS"

**Síntoma**
- Aviso de diferencia entre versos esperados y versos numerados.

**Causa habitual**
- Hay secuencias de verso partido mal cerradas.
- Se incrementó la numeración en un tramo que no quedó bien resuelto.

**Solución rápida**
- Corrige primero los avisos de versos partidos incompletos.
- Vuelve a validar hasta que desaparezca el desajuste.

## 6) "⚠️ LAGUNA DETECTADA" / "⚠️ VERSO CON CORCHETES DETECTADO"

**Síntoma**
- Avisos sobre posible uso incorrecto de `Laguna` o de `Verso` con corchetes.

**Causa habitual**
- Duda entre marcar pérdida incierta (`Laguna`) o un verso concreto omitido (`Verso` con corchetes).

**Solución rápida**
- Usa `Laguna` cuando no conoces cuántos versos faltan (no debe contar en numeración).
- Usa `Verso` con corchetes cuando representa un verso concreto que sí debe contar.

## 7) "❌ Formato incorrecto en archivo ..."

**Síntoma**
- Mensajes de formato incorrecto en `Notas` o `Aparato crítico`.

**Causa habitual**
- Párrafos que no empiezan por formato válido.
- Símbolo incorrecto para clave léxica (`@` en aparato o `%` en notas).

**Solución rápida**
- Usa una entrada por párrafo con prefijo válido: `NÚMERO:`, `NÚMERO+LETRA:`, `@palabra:` o `%palabra:`.
- En texto principal, respeta correspondencias: `@palabra` (nota), `%palabra` (aparato), `@%palabra` (ambas).

## 8) "Error en la conversión" (entrada inválida o incompleta)

**Síntoma**
- La conversión se detiene con mensaje de error en GUI.
- Mensajes típicos: archivo principal no válido/no existe, falta `Titulo_comedia`, metadatos inexistentes o con menos de 3 tablas.

**Causa habitual**
- El archivo principal no es `.docx` o no está disponible en la ruta indicada.
- El DOCX principal no contiene ningún párrafo con estilo `Titulo_comedia`.
- El DOCX de metadatos no existe o no cumple estructura mínima.

**Solución rápida**
- Verifica ruta y extensión de todos los archivos de entrada.
- Asegura que el principal incluye al menos un `Titulo_comedia`.
- Si usas metadatos, confirma que el documento tiene 3 tablas y está en su campo correcto.

---
> Si tu incidencia no aparece aquí, abre un issue con el mensaje exacto y un fragmento mínimo reproducible del DOCX: [GitHub Issues](https://github.com/prolopeuab/feniX-ML/issues).
> Próximamente ampliaremos esta sección con más casos reales.
{: .note }
