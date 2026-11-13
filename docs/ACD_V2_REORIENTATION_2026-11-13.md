# ACD V2 — Reorientación tras E0033 (13 de noviembre de 2026)

## Pregunta principal

¿Podemos superar a OIDN en la fidelidad de detalles arquitectónicos reales sin introducir ruido, halos, pérdida HDR ni coste computacional injustificado? La investigación deja de generar variantes de composición indiscriminadamente y pasa a diagnosticar fallos concretos.

**Evidencia que motiva el giro:** E0013, E0016 y E0021 muestran ACD Standard prácticamente equivalente al nodo OIDN del compositor, mientras High/Super no mejoran de forma consistente. Emission50 mejora HDR localizado en E0027/E0029, con regresión de gradientes; en Modern Hall E0033 (otro autor), OIDN tiene RMSE global 0.02223804 frente a 0.02230239 de Emission50, también peor error de bordes. Las referencias de 1024 spp difieren en RMSE 0.02153122. No hay ventaja visual general validada.

## Fases con puertas exigibles

**B0 — Consolidar el baseline.** Producción Blender 5.2.4 LTS; compatibilidad Blender 5.3.0; 5.0.1 como referencia histórica. Ambos lanzamientos oficiales son del 10-11-2026. Separar:
- OIDN en nodo compositor (Prefilter Accurate, Quality High, HDR, albedo y normal; baseline histórico E0013).
- Denoising integrado de Cycles (ruta independiente, todavía no medido en comparativa controlada ACD V2).
- OIDN standalone 2.5.1 con las mismas matrices RGB/albedo/normal y parámetros verificados.
- OptiX cuando haya GPU pertinente, y SID4 histórico; no atribuir capacidad SID5 al código SID4.
- Blender 5.3 ofrece DLSS de viewport temporal/upscale, no se considera equivalente a filtro de imagen final de Cycles sin protocolo propio.

B0a: smoke de compatibilidad de scripts, sockets de denoise y render Cycles en 5.2.4 y 5.3.0, con SHA256 oficial, hashes de AOV e igualdad de input dentro de cada versión. Referencia deliberadamente insuficiente para calidad. B0b: cotejar ruta interna Cycles frente al compositor y OIDN standalone bajo condiciones comparables, controlando versiones de biblioteca, flags, passthrough y costes. **No atribuir a OIDN diferencias de píxeles entre renders de versiones distintas.**

**B1 — Corpus representativo.** Escenas de arquitectura con PBR, geometría fina, vidrio, reflejos, vegetación, zonas oscuras y emisión a resolución >=1920 px. Mantener varias procedencias, casos sintéticos de fallo y división train/dev/test por escena y autor. Las escenas ya usadas (Cozy, Terraced, Island, Modern Hall) están observadas y no son tests ciegos. Licencias verificadas; escena personal fuera del repo público.

**B2 — Calidad de referencia y percepción.** Escalera de muestras, referencias independientes y evaluación de convergencia por región, estimando incertidumbre; pares de imágenes con el mismo raw/seed. RMSE/MAE HDR, error de gradiente, HDR-FLIP con condiciones publicadas, revisión visual 1:1 con OCIO/AgX coherente, diagnóstico de halos/fireflies, y calidad por tiempo total comparada con aumentar muestras de Cycles. No declarar ganador en diferencias menores que la incertidumbre observada.

**B3 — Hipótesis causal sobre guías.** Identificar fallos OIDN reproducibles en detalle arquitectónico, glossy/transmisión. Auditar origen y prefiltrado de normales/albedo (hits relevantes en Cycles), y proponer ablation de una variable con inputs idénticos. Preinscribir criterio y escenas retenidas antes de implementación. Priorizar guías y señal disponible sobre otra cadena de OIDN arbitraria.

**B4 — Promoción o descarte.** Solo con mejora fidelidad/percepción reproducible en holdout, sin regresión importante ni coste irracional, integrar al addon. Caso contrario registrar resultado negativo.

## Qué se pausa

- Emission50/100: congelados como hipótesis HDR localizada, sin reoptimización sobre las escenas ya observadas.
- High/Super: conservar como comparadores históricos, sin nuevos modos hasta detectar un mecanismo de error.
- Fork/reentrenamiento OIDN, superresolución y fotos: otras investigaciones, no requisitos de B0–B4.
- Benchmarks pesados automáticos: solo disparo manual y con propósito fijo. CI automática únicamente tests livianos de contrato.
- No fusionar PR #10 draft ni alterar addon estable.

## Trazabilidad y recuperación

Mantener resultados negativos, hashes, versiones, licencias y visuales PNG en GitHub. Los EXR/AOV de GitHub Actions vencen; no llamarlos almacenados permanentemente. Un informe de experimento + estado de hito + decisión, sin repetir resultados en infinitas notas.

**A fecha de este commit:** B0a se empieza por E0035 (compatibilidad de interfaz y tiny Cycles); todavía no existen pruebas reales de Blender 5.2.4/5.3.0 en el laboratorio. B0b/B1/B2/B3/B4 pendientes.

Versiones: https://www.blender.org/releases/ ; archivos oficiales: https://download.blender.org/release/Blender5.2/ y https://download.blender.org/release/Blender5.3/ .
