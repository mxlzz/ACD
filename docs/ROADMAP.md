# ACD — Roadmap de investigación y desarrollo

**Documento rector del plan.** Revisión inicial: 2026-11-11. Vigente para la rama `dev/acd-m2-real-scenes-regions`.

Este plan es una **referencia revisable**, no un calendario ni una promesa de superioridad. Cada hito requiere evidencia para avanzar. Las prioridades y el esfuerzo relativo pueden cambiar cuando los experimentos contradigan una hipótesis.

## Objetivo y límites

Desarrollar un sistema de reconstrucción para Blender/Cycles capaz de comparar y, cuando sea demostrable, mejorar la calidad obtenida a igual presupuesto de muestras frente al denoising nativo. El primer producto será un denoiser de **fidelidad radiométrica** para renders estáticos. La superresolución y el tratamiento de fotografía serán módulos posteriores que compartirán infraestructura de evaluación, **no necesariamente el mismo modelo de ruido**.

- La referencia pública estudiada de Super Image Denoiser es el código histórico disponible en GitHub. **No se ha demostrado equivalencia con SID comercial 5.3.**
- Un mejor RMSE en una escena **no** prueba superioridad general ni superioridad perceptual.
- La capacidad de ejecutar un nodo en Blender **no** prueba que la imagen resultante sea correcta.
- Las referencias finitas de 1024/4096 spp no son automáticamente ground truth convergido.
- Para la investigación fuente, evidencias e hipótesis véase [research_foundations.md](research_foundations.md).

## Control de rumbo en cada cambio

**Protocolo exigible:** [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md). **Registro de decisiones por commit:** [DECISION_LOG.md](DECISION_LOG.md). La CI comprueba que cada nuevo commit actualice conjuntamente roadmap, estado y bitácora. Esta verificación **no reemplaza** el juicio técnico ni las pruebas de Blender.

**Hito activo:** M3 / [Issue #7](https://github.com/mxlzz/ACD/issues/7), port fiel del SID público a Blender 5.x. **Primer requisito pendiente:** definir topología y configuración exactas de los grafos Standard/High/Super del SID público, incluidas ramas opcionales y licencias. **Siguiente puerta:** modo SID Reference probado con Blender 5, separado del ACD experimental.

## Prioridad rectificada: replicar SID antes de optimizar ACD

La implementación actual `addon/acd_blender.py` está **inspirada en** SID, pero no es un port fiel. La [auditoría de diferencias](sid_parity_gap.md) detectó desajustes concretos (prefiltrado Standard, guías de emisión, alfa, lectura de Noisy Image y semántica de nodos). **La prioridad inmediata pasa a ser M3 (Issue #7)**: construir un modo de referencia SID 4.0 históricamente fiel en Blender 5.x y verificarlo, **antes** de declarar alguna mejora de ACD sobre SID. Los benchmarks M2 siguen disponibles como infraestructura y datos; los ensayos de optimización M4 quedan pospuestos hasta tener baseline de SID validado. El código actual no debe denominarse réplica fiel.

## Escala de esfuerzo relativo

**S** = cambios localizados y pruebas automáticas; **M** = varias piezas de código y nuevos datos de prueba; **L** = experimentación significativa, dependencia de escenas/referencias, posible trabajo GPU; **XL** = investigación abierta o entrenamiento/integración con otros motores. Estas etiquetas NO indican fechas ni duración asegurada.

## Etapas, dependencias y condiciones de salida

| Hito | Estado | Prioridad | Esfuerzo | Condición de salida verificable |
| --- | --- | --- | --- | --- |
| **M0 — Base de ACD Core + Lab** | **Completado**, PR #1 fusionado | Cerrado | M | Addon experimental, laboratorio numérico, smoke de Blender y CI |
| **M1 — EXR y comparación controlada** | Implementado experimentalmente, PR #3 abierto | Alta | M | EXR/AOV con reconstrucción verificada, resultados por método y metadatos, tests verdes; después fusionar si pasa revisión |
| **M2 — Escenas reales y análisis regional** | En curso, PR #4 abierto | Media (infraestructura de M3) | L | Dos o más escenas complejas reproducibles, ROIs, diferentes muestras **verificadas**, evaluación de referencias y casos fallidos |
| **M2.1 — Validez estadística del laboratorio** | En curso / requisito de M2 | Alta (soporte de M3) | M–L | Control explícito de independencia/diversidad de ruido y de referencias, muestreo multi-escena y congelación de datasets |
| **M3 — Réplica funcional de SID público 4.0 para Blender 5.x** | Prioridad rectificada, Issue #7 | **Máxima (ahora)** | L | Auditar fidelidad al SID público por etapas, HDR/alpha/reflejos/transmisión, con comparaciones justas a OIDN/OptiX |
| **M4 — Fusión adaptativa, H-01/H-03** | Hipótesis | Alta, tras M2/M3 | L–XL | Pesos locales/pasada por componente probados en escenas y semillas no usadas para calibrar; evidencias y ablaciones |
| **M5 — Estadística y muestreo, H-04** | Investigación | Media, tras M4 | XL | Buffers de incertidumbre confiables; prueba contra multimuestreo de igual presupuesto y contra filtros existentes |
| **M6 — Upscale HDR de renders, H-05** | Diseño futuro | Media, tras M3/M4 | L–XL | Comparación 2× contra bicúbico/Lanczos y método aprendido con referencia renderizada realmente a resolución alta |
| **M7 — Fotografía/RAW, H-06** | Diseño futuro | Baja por ahora | XL | Pipeline distinto para ruido fotográfico, datasets con referencia, control de color y resultados por objetivo de fidelidad/percepción |
| **M8 — Producto y distribución** | Futuro | Depende de resultados | L | API/instalador estable, rendimiento, perfil de calidad reproducible, licencias y compatibilidad Blender |

### M2 / M2.1: soporte del benchmark; subordinado a la validación SID/M3

**Seguimiento operativo:** [Issue #5 — Validez de muestreo, referencias y métricas](https://github.com/mxlzz/ACD/issues/5). El issue incluye los criterios de aceptación y evidencia que deben cerrarse antes de atribuir mejoras de calidad al algoritmo.

**Avance M2.1 (2026-11-11):** control de máscaras con SHA-256 por pertenencia real de píxeles, diagnóstico de incertidumbre de referencias finitas y comprobación de diversidad de inputs sin declarar independencia estadística. Pruebas automatizadas añadidas y E0008 repetido íntegramente con resultados reproducidos ([E0010](experiments/E0010.md)). La segunda escena procedural de vidrio y metal ([E0011](experiments/E0011.md)) favoreció a Standard; aún faltan escenas profesionales externas y convergencia de referencia.

1. **Cerrar las anomalías de muestreo de Classroom (E0007):** ninguna estadística multi-seed es válida por el solo hecho de cambiar un número. El laboratorio ya bloquea rankings cuando imágenes supuestamente distintas son casi idénticas. Investigar causa; no dar por demostrado el efecto con el chequeo heurístico de diversidad solamente.
2. **Revalidar el agregador regional (E0008):** repetir el flujo completo después de corregir el bug `seed_aggregate.json` interpretado como carpeta; documentar la máscara fija y las diferencias de MAE/RMSE. Mantener sin activar por defecto la preservación de emisión.
3. **Obtener una segunda escena arquitectónica exigente** (vidrio/especular/indirecta) con licencia y procedencia registradas, sin subir assets ajenos a Git. Repetir AOV closure, muestras verificadas y 2 referencias con distinta secuencia de muestreo.
4. **Subir progresivamente a resoluciones representativas** y ajustar las muestras según convergencia, sin gastar CPU en referencias que no permitan comparar métodos con precisión.
5. **Análisis por región:** vidrio, metal, superficies difusas, iluminación indirecta y emisores. Usar ROI fijadas antes de ver resultados y AOV como diagnóstico de contribución, no como IDs de materiales.
6. **Añadir métrica perceptual HDR** con condiciones de exposición declaradas, además de RMSE/MAE/p95, y revisar recortes a tamaño nativo.
7. **Cerrar o descartar hipótesis fallidas:** las conclusiones negativas también quedan documentadas y no se incorporan al motor.

**E0012:** [Ablación de guías Albedo/Normal](experiments/E0012.md): High mejora sin guías intermedias, Super no. Normal sin Albedo no es válido en OIDN de Blender. La [auditoría del código de Cycles v5.0.1](cycles_guide_source_audit.md) demuestra que el renderer ya sigue ciertos rebotes especulares; H-01 ahora investiga la correspondencia de guías por subpase en lugar de duplicar esa lógica. Seguimiento operativo: [Issue #6](https://github.com/mxlzz/ACD/issues/6).

### M3: replicar SID público y normalizar su evaluación

**Issue principal:** [#7 — Réplica SID 4.0 para Blender 5.x](https://github.com/mxlzz/ACD/issues/7). Diferencias auditadas en [sid_parity_gap.md](sid_parity_gap.md). La prioridad es funcional (grafo, parámetros, passes y outputs), **antes** de comparar calidad o desarrollar filtros nuevos.

- Configurar exactamente la semántica de las contribuciones directas/indirectas y la segunda pasada tal como aparece en el SID público; comparar también emisión y alfa. La documentación del algoritmo **no** garantiza reproducir el código comercial.
- Registrar versiones OIDN, Blender, prefiltrado, guías, render backend, memoria y tiempo. Evitar comparar configuraciones o sample counts diferentes.
- Incluir OIDN nativo, OptiX nativo cuando la GPU esté disponible, Standard/High/Super y ablaciones con/sin guías por contribución.
- Criterio de salida: evidencia reproducible sobre varias escenas y semillas, mostrando también pérdidas en regiones donde cada modo falla.

### M4: hipótesis adaptativas (investigar, no prometer)

- **H-01:** condicionamiento de guías por tipo de señal (un normal/albedo del primer hit puede no representar el detalle dentro de reflejos o de cada pase).
- **H-03:** una fusión por región/píxel, con pesos calculados sin mirar la referencia de test, puede mejorar la curva error-tiempo en imágenes no vistas.
- Baselines obligatorios: mejor modo global fijo, interpolaciones fijas, mapas aleatorios/constantes, ablation sin guía.
- Bloquear sobreajuste: separar conjuntos de calibración, validación y prueba por **escena**, no solo por píxel.
- Si no mejora en datos no vistos, no se integra; volver a M3 o rediseñar la hipótesis.

### M5 a M7: exploraciones sin compromiso de adopción

- **M5:** StatER/StatMC proponen estadísticas por muestra que Cycles no entrega directamente en el EXR usual. Comenzar por muestreos pareados y mapas de varianza estimada; la integración dentro del renderer es una opción avanzada, no una dependencia inicial.
- **M6:** distinguir nitidez inferida de detalle realmente recuperado. Probar modelos específicos de upscale y/o OptiX SDK (la disponibilidad del SDK no implica una opción idéntica en el nodo de Blender).
- **M7:** OIDN `RT` está documentado para imágenes de ray tracing, no para ruido de cámara. Reusar la infraestructura, con algoritmos de fotografía/RAW específicos y benchmark aparte.

## Reglas de promoción de una modificación al producto

1. **Corrección funcional:** sintaxis, pruebas y Blender real pasan; no alterar archivos de producción sin backup.
2. **Validez científica:** inputs comparables, seed-diversity y referencia controladas, métricas y recortes auditables.
3. **Calidad consistente:** mejora frente a un baseline definido sin una regresión importante en una clase relevante de materiales o región; registrar también tiempo y memoria.
4. **Reproducibilidad:** commit, scene hash, Blender version, AOV, muestras, semillas/patrón, imagen lineal y JSON de resultados quedan identificados.
5. **Revisión de licencia:** código de terceros, pesos, datasets y archivos `.blend` pueden tener licencias distintas.

## Registro persistente y actualizaciones

- **Este archivo:** qué se pretende hacer y por qué prioridad.
- [research_foundations.md](research_foundations.md): evidencia externa y matriz de trazabilidad entre fuentes e hipótesis.
- [STATUS.md](../STATUS.md): último estado observado; jamás sustituirlo por planes futuros.
- [experiments/](experiments/): pruebas E0001+, incluyendo hallazgos negativos y limitaciones.
- Issues / PR: implementación y validación antes de fusionar.

Al cerrar una etapa o cambiar de dirección, actualizar **STATUS**, este roadmap y las entradas de investigación asociadas. No inferir que una tarea está terminada por la existencia de código o de una ejecución de Actions.
