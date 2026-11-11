# Protocolo obligatorio de avance de ACD

Vigencia desde: 2026-11-11. Se aplica a **cada commit posterior a la introducción de este archivo**.

## Objetivo vigente

**M3 / Issue #7: portar con fidelidad el SID público a Blender 5.x antes de optimizar ACD.**

Cadena de objetivos que no debe invertirse:

1. Fijar versión/commit, licencia y especificación completa del grafo del SID público.
2. Implementar un modo **SID Reference** fiel y separado del experimento ACD.
3. Verificar paridad de nodos, conexiones, parámetros, salidas y calidad contra SID original, explicitando diferencias entre Blender/OIDN.
4. Solo entonces reanudar hipótesis de mejoras adaptativas, superresolución y nuevos filtros, con el laboratorio como respaldo.

La investigación M1/M2 sigue siendo útil como infraestructura; no desplaza la prioridad M3. No presentar el prototipo actual como SID reproducido. No copiar código GPL en ACD sin resolver primero el esquema de licencia y atribución.

## Cada cambio: procedimiento operativo

**Antes del cambio**
1. Leer [ROADMAP.md](ROADMAP.md), [STATUS.md](../STATUS.md), [sid_parity_gap.md](sid_parity_gap.md) y este protocolo; identificar el hito vigente y el primer requisito pendiente.
2. Declarar cuál es el **objetivo verificable** del cambio y vincularlo con un issue/hito. Si no sirve M3 ni un prerequisito explícito, **no ejecutarlo** sin justificar y registrar una modificación de rumbo.
3. Establecer la prueba de aceptación **antes** de cambiar el código. Si la hipótesis no está corroborada, marcarla como tal.

**Después del cambio, en el mismo commit**
4. Ejecutar tests relevantes (Python, Blender headless y/o render cuando el cambio lo exija). Nunca convertir una CI pendiente en prueba aprobada.
5. Actualizar **simultáneamente**:
   - [ROADMAP.md](ROADMAP.md): etapa, prioridad, siguiente paso y dependencias; si permanece igual, consignar explícitamente que se revalidó.
   - [STATUS.md](../STATUS.md): qué fue implementado, qué está efectivamente verificado, qué falló y qué queda pendiente.
   - [DECISION_LOG.md](DECISION_LOG.md): decisión, vínculo al hito, prueba, resultado real, desviaciones y siguiente acción.
6. Cuando corresponda, actualizar auditorías, estudios o experimentos E00xx, sin modificar retroactivamente resultados históricos.
7. Si falló una prueba o apareció una discrepancia con SID, detener la promoción al modo de referencia, abrir/actualizar issue y registrar la observación antes de corregir.
8. **Rechequear alineación:** ¿sigue sirviendo al hito M3 y al objetivo de fidelidad SID? ¿Se mantiene separado del prototipo? ¿El próximo paso sigue siendo el más prioritario? Si una respuesta es no, justificar en el registro de decisiones y corregir el roadmap **antes de avanzar**.

## Protección automática

La CI ejecuta \`scripts/check_development_trace.py\`, que revisa cada commit **no-merge posterior al commit que incorpora este protocolo**. Exige que dicho commit toque los tres archivos \`docs/ROADMAP.md\`, \`STATUS.md\` y \`docs/DECISION_LOG.md\`. Aplica incluso a cambios documentales: la trazabilidad no depende de memoria de chats.

La automatización verifica **presencia de actualizaciones**, no su calidad, veracidad, alineación o resultados científicos. La revisión argumental de cada paso sigue siendo obligatoria. Si la prioridad cambia legítimamente, registrar por qué y reordenar las etapas con un commit que actualice los tres documentos.

**No fusionar** experimentos ni declarar equivalencia a SID mientras no exista evidencia de paridad. **No consumir Actions de render pesado en cada commit**: usar CI ligera por defecto y benchmarks manuales en puntos de decisión.

## En caso de interrupción o cambio de chat

Abrir, en este orden: \`docs/ROADMAP.md\` → \`STATUS.md\` → \`docs/DECISION_LOG.md\` → issue vigente. Continuar desde el primer criterio de aceptación incumplido, no desde la última idea conversada.
