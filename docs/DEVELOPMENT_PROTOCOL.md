# Protocolo obligatorio de avance de ACD — revisión V2

Vigente desde **2026-11-12** por [Issue #9](https://github.com/mxlzz/ACD/issues/9). [Programa rector V2](ACD_V2_PLAN.md). Sustituye la antigua obligación de *priorizar paridad SID 4.x*, que queda satisfecha hasta el alcance medido en E0013, **sin afirmar equivalencia con SID 5.x**. El resto de los experimentos permanece en el historial y sin modificación retroactiva.

## Prioridad vigente
1. OIDN nativo de Blender 5 como baseline operativo explícito; OIDN standalone y OptiX como variantes con hardware disponible; SID4 público como comparador histórico y SID5.x solo con acceso reproducible al software original.
2. Antes de diseñar una mejora, diagnosticar el error real sobre beauty, HDR y detalle, usar mapas/recortes contra referencias y repetir en escenas diversas.
3. Antes de entrenar pesos o bifurcar OIDN, estudiar implementaciones externas, verificar licencias, evaluar cambios incrementales y la accesibilidad de datos por muestra.
4. Mantener experimentos aislados del addon estable; no fusionar sin prueba representativa, validación por escena no vista y evaluación de recursos.

## Procedimiento exigible en *cada commit*
- Leer [ROADMAP.md](ROADMAP.md), [STATUS.md](../STATUS.md), [DECISION_LOG.md](DECISION_LOG.md) y el Issue #9. Fijar hipótesis, prerequisitos, prueba de aceptación y clasificación de evidencia (estático, test sintético, Blender real, benchmark real).
- Tras la modificación actualizar **en el mismo commit** `docs/ROADMAP.md`, `STATUS.md`, `docs/DECISION_LOG.md`. El comprobador `scripts/check_development_trace.py` exige estos tres archivos desde la activación histórica del protocolo.
- Documentar código, hashes y versiones, licencia de dependencias, método de referencia, número de muestras, seeds y validez de ranking; CI de Python solo confirma integridad/test, no calidad científica.
- No inferir independencia de seeds por valores distintos ni convergencia por dos referencias cercanas; no tratar nitidez, gradientes o RMSE aisladamente como evidencia de detalle recuperado.
- Auditorías, resultados negativos y problemas de tests se conservan; los artifacts que caducan son un suplemento, no la única fuente.
- Trabajo pesado solo en workflows manuales/de decisión. Mantener PRs experimentales en draft y no publicar escenas propietarias.

## Recuperación entre chats
Leer [ACD_V2_PLAN.md](ACD_V2_PLAN.md) → [STATUS.md](../STATUS.md) → [DECISION_LOG.md](DECISION_LOG.md) → [Issue #9](https://github.com/mxlzz/ACD/issues/9); ejecutar primero el prerequisito sin verificar. El [roadmap histórico](ROADMAP.md) conserva hitos SID y experiencias anteriores para trazabilidad, sin prioridad operativa actual.
