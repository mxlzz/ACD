> **NUEVA PRIORIDAD 2026-11-12:** [ACD V2 — OIDN y evaluación de detalle](ACD_V2_PLAN.md), [Issue #9](https://github.com/mxlzz/ACD/issues/9). El programa histórico M3/SID a continuación se conserva por trazabilidad y **ya no es la puerta obligatoria hacia mejoras**. Se revalidó la pertinencia de la infraestructura M1–M3 y E0013. F1 en proceso (documentación/CI pendiente), F2 auditoría estática iniciada, F3 métricas de detalle pendientes. No se modificó producción.

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

**Hito activo:** M3 / [Issue #7](https://github.com/mxlzz/ACD/issues/7). La especificación [M3_SID_REFERENCE_SPEC.md](M3_SID_REFERENCE_SPEC.md) y el constructor independiente `addon/sid_reference.py` están implementados en la rama experimental; no reemplazan al addon estable.

**Puertas comprobadas en Actions (2026-11-11):** [quality gate #43098851163](https://github.com/mxlzz/ACD/actions/runs/43098851163), [Blender 5.0.1/5.3 smoke #43098851162](https://github.com/mxlzz/ACD/actions/runs/43098851162), y [SID 3.6 original vs port 5.0 graph contract #43098851161](https://github.com/mxlzz/ACD/actions/runs/43098851161) terminaron correctamente. Este último reportó `passed=true`, `errors=[]`, solo para invariantes estructurales limitados. 5.3 omite benchmarks pesados por configuración.

**Puertas verificadas después de la corrección:** [contratos SID 3.6/5.0 #43101708644](https://github.com/mxlzz/ACD/actions/runs/43101708644) `success` con artifact de **tres JSON** ([descarga](https://github.com/mxlzz/ACD/actions/runs/43101708644/artifacts/13890459701)); [quality gate #43101708666](https://github.com/mxlzz/ACD/actions/runs/43101708666) `success`; [Blender smoke #43101708862](https://github.com/mxlzz/ACD/actions/runs/43101708862) `success` en 5.0.1/5.3. Los runs antiguos en cola no explican por sí solos el origen del problema (Issue #8), que ya no bloquea las pruebas nuevas.

**M3.5 Standard observado:** run [43104673773](https://github.com/mxlzz/ACD/actions/runs/43104673773) \`success\` con 3 entradas EXR exactamente idénticas en passthrough. Diferencia RGB Standard RMSE 0.03285426 (HDR RMSE 0.04103480); alfa RMSE 0, sin demostración de paridad píxel ni superioridad. Artifact conservado en el run.

**M3.6 operadores sin OIDN validados:** [run 43106813982](https://github.com/mxlzz/ACD/actions/runs/43106813982) `success`. ADD/MULTIPLY/HDR idénticos en RGB/alfa, y recombinación alfa diferencia máxima ~5.96e-08. Se descarta una gran brecha de estas operaciones en el fixture de prueba, no en todas las combinaciones posibles.

**M3.7 OIDN aislado aprobado (evidencia real):** [run #43107260820](https://github.com/mxlzz/ACD/actions/runs/43107260820) y [artifact #13895310157](https://github.com/mxlzz/ACD/actions/runs/43107260820/artifacts/13895310157), control de entrada válido. Diferencias RGB RMSE interversiones: Fast guiado 0.03285428 (coincide con Standard integral 0.03285426), Accurate guiado 0.03060210, emisión Accurate sin guías 0.06191731, alfa RGB guiada 0.00618145, Diffuse Direct 0.00425341. Emisión ROI HDR 0.21570960 (High/Super globales en esa región 0.22306/0.23224). M3.6 ya había verificado identidad práctica de operaciones de mezcla.

**M3.8 error de sintaxis del workflow observado:** [run #43111531413](https://github.com/mxlzz/ACD/actions/runs/43111531413) terminó antes de crear jobs; un nombre de paso con `Archive matrix: EXRs` tenía un `:` sin entrecomillar. Corrección localizada al YAML; el experimento aún no se ejecutó. No se modifica metodología por un error de orquestación.

**M3.8 resultados CI comprobados:** [run 43111684409](https://github.com/mxlzz/ACD/actions/runs/43111684409) y [artifact 13896511879](https://github.com/mxlzz/ACD/actions/runs/43111684409/artifacts/13896511879) con 8 legacy + 24 port. Blender5 OIDN 2.3.3 localizado. HDR=false acerca algunas salidas históricas, pero produce grandes cambios en emisiones dentro de Blender5 (RMSE 0.9046); no falsear radiancia con esa configuración.

**M3.9 primera corrida completada, evidencia no concluyente:** [run 43112553045](https://github.com/mxlzz/ACD/actions/runs/43112553045). Glass Lobby: ACD Standard/OIDN compositor RMSE idéntico 0.14789 vs Raw 0.32117, referencias 384 spp discrepancia relativa 0.31496 (alerta). Classroom: noisy seeds y refs prácticamente idénticas, control de diversidad falla; no establecer ranking multisemilla. Mejorar protocolo antes de tomar decisiones algorítmicas.

**M3.9 segunda corrida ejecutada — no se demostró ventaja sobre OIDN nativo:** [CI #43113414513](https://github.com/mxlzz/ACD/actions/runs/43113414513), tres seeds y dos refs de 1024 spp en Glass Lobby e interior emisivo. Ambos pasan cribado de diversidad (no prueba de independencia/convergencia). RMSE medio Glass: Standard/OIDN 0.14833401, High 0.17022242, Super 0.17611973; emisivo: Standard/OIDN 0.08236044, preservación emisión 0.08267392, High 0.08670461, Super 0.09241571. Variantes SID4 tampoco superaron nativo. Datos detallados y limitaciones en [E0013](experiments/E0013.md). El incidente Classroom ya estaba en E0007: evitar reiteración de pruebas inválidas.

**Siguiente requisito de calidad:** recibir un `.blend` real de arquitectura autorizado y representativo, con recursos empaquetados, para probar ACD fuera de los fixtures de desarrollo. [Protocolo de ingreso](PRO_SCENE_INPUT.md) y runner local existente `scripts/run_scene_benchmark.py`. Ningún cambio algorítmico en producción hasta definir una hipótesis con validación fuera de escena. **No fusionar PR #4**.

**M3.9 segunda corrida candidata:** sustituir Classroom inválido por `interior_emissive`, referencias 1024 spp ×2 con semillas distintas y 3 low-spp noisy seeds, activar ablación preexistente preservación de emisión. Registrar la diferencia directa ACD vs nativo y SID4 para descubrir candidatos redundantes. Incluir flags de validez que impidan conclusiones cuando semilla/reference fallan. **CI pendiente**.

**M3.9 preparado, pendiente CI:** dos escenas Cycles (glass_lobby procedural y Classroom CC0), 160×120, low spp 24×2 semillas; dos referencias independientes de 384 spp; medir SID4 Standard/High/Super, ACD Standard/High/Super y nodo nativo OIDN compositor sobre los mismos pixels. Revisar coincidencia de rankings entre referencias y dispersión entre seeds; esto sigue siendo piloto de baja resolución, no superioridad certificada.

**M3.8 ensayo configuracional implementado, resultado pendiente:** Nuevo workflow `sid-oidn-parameter-matrix.yml`: 4 filtros × HDR on/off × Quality High/Balanced/Fast Blender5 (24 outputs) contrastados contra 8 salidas correspondientes de Blender3.6. Las fuentes oficiales distinguen `Prefilter`, HDR y Quality; la última opción no es configurable del mismo modo en Blender3.6. Registrar deltas *entre implementaciones* y efectos de cambios *dentro de Blender5*, sin llamar “mejor” al candidato que más se parezca al histórico. Guardar inputs, hashes, EXR, mapas. CI pendiente.

**Siguiente gate M3.8:** auditar diferencias OIDN de versión/configuración y ensayar ablaciones de `Prefilter`, `Quality`, `HDR` con exactamente el mismo EXR, sin forzar convergencia visual por afinado arbitrario; luego validar contra escenas Cycles complejas y referencias suficientemente convergidas. **No promover M3 ni fusionar PR #4 por coincidencia estructural o un solo fixture sintético.**

**M3.7 próximo control:** OIDN directo aislado, con prefilters Fast/Accurate, guías, emisión y alfa, inputs EXR congelados. Nuevo workflow `sid-oidn-numeric-parity.yml` candidato; CI pendiente al commit. Este experimento deberá determinar si las divergencias se manifiestan antes de ensamblar High/Super, pero no certifica causa exacta ni versión OIDN equivalente.

**M3.5 High/Super medidos:** [CI #43106273482](https://github.com/mxlzz/ACD/actions/runs/43106273482) completada, artefacto EXR/NPZ [13894002202](https://github.com/mxlzz/ACD/actions/runs/43106273482/artifacts/13894002202). Passthrough de 15 AOV válido. High RGB RMSE 0.06531013, Super 0.06788146; región emisiva High 0.22305557 y Super 0.23223786; alfa global ambos ~0.0038727. **No es comparación contra ground truth** ni identifica causas de diferencias.

**M3.6 objetivo inmediato:** descartar/medir diferencias de operaciones del compositor (MixRGB → ShaderNodeMix ADD/MULTIPLY/HDR; SepRGBA/CombRGBA → SetAlpha), sin OIDN, usando entradas EXR congeladas y salidas comparables. Implementación del workflow `sid-operator-numeric-parity.yml` como candidato, CI pendiente. Solo después aislar cambios de backend OIDN y realizar test con escenas reales.

**M3.5 fallo de orquestación observado:** en [run 43106081661](https://github.com/mxlzz/ACD/actions/runs/43106081661), pytest del fixture aprobó pero la invocación directa de script impidió importar el namespace `scripts`. Ajustar comando a `python -m scripts.sid_highsuper_numeric_fixture` y equivalente de comparador; no cambiar datos, grafo ni tolerancias. Nueva CI pendiente.

**M3.5 High/Super siguiente prueba:** workflow \`sid-highsuper-numeric-parity.yml\` preparado con 15 AOV, datos congelados, controles de lectura por Blender y diferencias RGBA/ROI. **CI pendiente**. Si pasa el control de entradas y genera métricas, registrar el alcance; no cerrar M3 sin analizar el backend y escenas reales.

**M3.5 observación real de CI:** [#43104453238](https://github.com/mxlzz/ACD/actions/runs/43104453238) ejecutó exitosamente upstream Standard en Blender 3.6, pero no el port Blender 5 porque OutputFile estaba por defecto en media MULTI_LAYER_IMAGE; `OPEN_EXR` solo se permite tras fijar `media_type="IMAGE"`. Corrección mínima en driver para Blender 5. **Reejecución pendiente; no interpretar todavía deltas del denoiser.**

**Refuerzo de método M3.5 (antes de resultados):** el control de passthrough se aplica por separado a imagen ruidosa, albedo y normal, con comparación entre versiones; las diferencias de ambos compositores respecto del EXR de origen se reportan, pero no se confunden con un efecto OIDN. Corrige además el conteo de píxeles sin máscara. El criterio de salida mantiene una tolerancia de entrada cross-version de 0.001 y salidas finitas. Este refinamiento no equivale a ejecución aprobada.

**M3.5 implementado como experimento candidato (verificar CI):** `.github/workflows/sid-numeric-parity.yml` genera imagen/albedo/normal en EXR lineal con SHA-256, ejecuta SID Standard upstream (Blender 3.6.23) y port Standard (5.0.1), guarda passthrough y outputs, reporta diferencias RGB HDR/alfa y mapas firmados. Su entrada sintética 96×64 no sustituye escenas Cycles. El control de passthrough (máx absoluto ≤0.001) evita atribuir al filtro diferencias en lectura/escritura. **CI aún pendiente al momento de este commit**. Una ejecución fallida no invalida el método sin inspeccionar sus logs. High/Super continuarán una vez confirmado Standard.

**Siguiente etapa M3.5 (criterio de aceptación):** ejecutar SID histórico en Blender 3.6 y SID Reference en 5.0 sobre **exactamente el mismo EXR/guías/AOV**. Guardar hashes de entrada, versiones, todos los outputs (RGB/alpha), mapas de error HDR, configuraciones OIDN y distinción explícita entre desviaciones de backend y desajustes de cableado. Empezar con Standard y luego High/Super; no probar optimización adaptativa ni declarar identidad pixel a pixel antes de medir. PR #4 permanece draft.

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
