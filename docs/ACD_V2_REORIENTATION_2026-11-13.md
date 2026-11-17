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


## Estado verificado B0a/B0b inicial — 2026-11-13

- B0a **aprobado** en Blender5.2.4/5.3.0 con E0035: contratos de API y compositor, identidad exacta de Raw vs EXR multilayer dentro de cada build. Diferencias entre builds en beauty, albedo y normal invalidan comparaciones de versión si se presupone el mismo input. Datos [E0035](experiments/E0035.md).
- B0b **primera comparación controlada terminada**: [E0036](experiments/E0036.md) obtiene Cycles interno y compositor desde un único render, RMSE entre salidas 1.4466e-7 (no bitwise match). Faltan OIDN CLI 2.5.1 en misma señal y perfil coste normalizado. No ampliar conclusiones a materiales/resolución profesional ni calidad.
- Próximo criterio de cierre B0: comparar CLI 2.5.1 con los exactos EXR y AOV a igual HDR/prefiltro, registrar condiciones; luego iniciar corpus B1 y convergencia B2. Mantener E0035/E0036 como contratos, no como ranking.


## 2026-11-13 — B0b: E0037–E0039 cerrados como diagnóstico, no como ranking

- E0037: OIDN standalone 2.5.1 en Raw/AOV congelados de Blender 5.2.4 y 5.3.0 difiere del compositor, RMSE ~0.04647 sin prefiltrado y ~0.04035 con filtros RT de guías + cleanAux. Las salidas no son rankings de calidad.
- E0038: OIDN oficial 2.5.0 vs 2.5.1 sobre los mismos PFM difiere ~0.0000020 RMSE, muy por debajo de la diferencia CLI vs Blender. Ambas releases de Blender compilan contra OIDN 2.5.0 según sus versions.cmake, pero equivalencia binaria/flags no garantizada.
- E0039: [run 43492225086, attempt 2](https://github.com/mxlzz/ACD/actions/runs/43492225086) **success**. EXR multilayer y salidas FileOutput directamente de RLayers Image (Raw), Denoising Albedo y Denoising Normal son idénticos (RMSE y delta máximo 0 por cada pase). Primer attempt falló por ausencia de socket Noisy Image al tener denoising Cycles apagado, segundo attempt inicialmente sufrió HTTP 403 transitorio y funcionó tras rerun. No se inventaron guías ni se modificó OIDN.
- **Decisión:** Blender 5.2.4 LTS compositor/Cycles ya es baseline funcional; mantener OIDN CLI como comparador distinto y la divergencia residual sin causalidad resuelta. No bloquear indefinidamente B1 por paridad de una interfaz externa en un fixture 128px; retomar solo si una hipótesis B3 necesita inferencia standalone. **No declarar B0b igualdad ni superioridad.**


# B1 — Corpus: inventario y aceptación de una escena arquitectónica realista

**Preinscrito 2026-11-13; primer candidato: Barcelona Pavilion.**

- Fuente oficial: [Blender Demo Files](https://www.blender.org/download/demo-files/), sección Cycles, Barcelona Pavillion, **eMirage**, **CC-BY (versión no especificada en el catálogo)**. Descarga histórica publicada en Blender: https://download.blender.org/demo/test/pabellon_barcelona_v1.scene_.zip . Se conservará licencia y atribución por separado; NO redistribuir el .blend hasta verificar sus contenidos y condiciones.
- Razonamiento: escena arquitectónica realista de autor distinto a Cozy Kitchen / Modern Hall / Island y Terraced Houses; candidata a observar juntas/reflejos, materiales y vidrio. El tamaño indicado en el catálogo es aprox. 24 MB, pero debe verificarse **contenido ZIP, recursos y cámara** antes de caracterizarla.
- Clasificación **desarrollo/calibración**, no holdout. Al inspeccionarla deja de ser una escena ciega. Reservar futuras escenas de otro autor/estilo para test fuera de muestra.
- [Workflow](../../.github/workflows/acd-b1-barcelona-smoke.yml): descargar ZIP sin publicarlo, registrar SHA256 y número/tamaño de entradas, controlar zip-slip, extraer en /tmp, localizar un .blend exacto, rechazar dependencias faltantes, abrir con Blender 5.2.4 --disable-autoexec, render Cycles CPU 192×192 **4 spp** sin denoising y conservar solo metadatos y PNG de smoke. No usar este smoke como medición de denoising ni compararlo con OIDN. Archivo fuente permanece fuera de Git y de los artifacts.
- **Aceptación:** SHA ZIP, estructura documentada, dependencias resolubles, cámara/materiales, Cycles smoke exitoso. Si no, registr

## 2026-11-13 — E0043: retorno al problema de calidad sin repetir anterioridad

- **Decisión de enfoque:** tras E0042 (RMSE interseed 128spp ≈0,05549), NO prolongar la escalera de referencias y NO inventar un nuevo filtro. Intel OIDN y Blender ya conocen variaciones sin guía / albedo / albedo+normal y prefilter; las comparaciones se usan solo para detectar una falla reproducible que pueda justificar investigación causal.
- [E0043_PLAN](docs/experiments/E0043_PLAN.md) congelado antes de ejecución: Italian Flat, 640x400, 32spp seed539, **un render nuevo** 3 nodos OIDN existentes con los mismos Raw y guías; dos referencias 128spp existentes recuperadas del run E0042, grilla fija 4x4 y controles de disparidad inter-referencia.  No se proclama mejora de algoritmo ni se modifica addon. Los resultados dependen de la ejecución del nuevo workflow.
- **Regla de descarte:** si las tres rutas conocidas no muestran un fallo interpretable/consistente con ambas referencias y con margen respecto a incertidumbre de referencias, suspender esta ablation sin más tuning ni referencias a ciegas. En tal caso avanzar a auditoría de modo de fallo de reflejos/transmisión ya documentado por OIDN, sin volver a implementarlo de cero.
